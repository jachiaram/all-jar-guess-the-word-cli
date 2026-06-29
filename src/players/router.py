from enum import Enum
import random
from pathlib import Path
import re
import sys

from fastapi import APIRouter, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..core.database import create_database_session, Base

app = APIRouter()


class MatchValue(str, Enum):
    full = "full"
    partial = "partial"
    none = "none"


class GameStatus(str, Enum):
    in_progress = "in-progress"
    won = "won"
    lost = "lost"


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class CurrentGame(Base):
    __tablename__ = "current_games"

    id = Column(Integer, primary_key=True)
    secret_word = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)

    guesses = relationship(
        "GameGuess", back_populates="current_game", cascade="all, delete-orphan"
    )
    result = relationship(
        "GameResult",
        back_populates="current_game",
        uselist=False,
        cascade="all, delete-orphan",
    )
    player = relationship("Player", back_populates="current_game", uselist=False)


class GameGuess(Base):
    __tablename__ = "game_guesses"

    id = Column(Integer, primary_key=True)
    current_game_id = Column(Integer, ForeignKey("current_games.id"), nullable=False)

    current_game = relationship("CurrentGame", back_populates="guesses")
    letters = relationship(
        "GuessLetter", back_populates="guess", cascade="all, delete-orphan"
    )


class GuessLetter(Base):
    __tablename__ = "guess_letters"

    id = Column(Integer, primary_key=True)
    guess_id = Column(Integer, ForeignKey("game_guesses.id"), nullable=False)
    letter = Column(String(1), nullable=False)
    match = Column(
        SAEnum(MatchValue, values_callable=enum_values),
        nullable=False,
    )

    guess = relationship("GameGuess", back_populates="letters")


class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True)
    current_game_id = Column(
        Integer, ForeignKey("current_games.id"), nullable=False, unique=True
    )
    status = Column(
        SAEnum(GameStatus, values_callable=enum_values),
        nullable=False,
    )
    word = Column(String, nullable=True)

    current_game = relationship("CurrentGame", back_populates="result")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    seen_words = Column(ARRAY(String), nullable=False, default=list)

    current_game = relationship("CurrentGame", back_populates="player", uselist=False)


class PlayerRegister(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str


class PlayerRead(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str
    current_game: "CurrentGameRead | None" = None


class PlayerIdentityRead(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str
    seen_words: list[str]


class LetterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letter: str
    match: MatchValue


class GuessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letters: list[LetterRead]


class GameResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: GameStatus
    word: str | None


class CurrentGameRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, populate_by_name=True
    )

    secret_word: str
    guesses: list[GuessRead]
    result: GameResultRead | None = None


class CurrentBoardRead(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    length: int
    guesses: list[GuessRead]
    result: GameResultRead | None = None


class UserBoardRead(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str


class PlayerBoardRead(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user: UserBoardRead
    current: CurrentBoardRead


PlayerRead.model_rebuild()


@app.post("", response_model=PlayerIdentityRead, status_code=201)
def create_player(
    player: PlayerRegister, db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(status_code=422, detail={"error": {"description": "Name is required"}})
    
    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, player.name):
        raise HTTPException(status_code=422, detail={"error": {"description": "Invalid player name"}})
        sys.exit(1)
        
    player_name = player.name.replace(" ", "").lower()

    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if existing_player:
        raise HTTPException(
            status_code=422, detail={"error": {"description": "Name must be unique"}}
        )

    db_player = Player(name=player_name, seen_words=[])
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player


@app.post("/sessions", response_model=PlayerIdentityRead, status_code=200)
def get_player_by_id(
    player: PlayerRegister, db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(
            status_code=422, detail={"error": {"description": "Name is required"}}
        )

    player_name = player.name.replace(" ", "").lower()

    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if not existing_player:
        raise HTTPException(
            status_code=422, detail={"error": {"description": "Player not found"}}
        )

    return existing_player


def access_denied_response() -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"error": {"description": "Access denied"}},
    )


def create_current_game_for_player(player: Player, db: Session) -> CurrentGame:
    words_path = Path(__file__).resolve().parent.parent / "word_list.txt"

    try:
        with words_path.open() as words_file:
            words = [line.strip().lower() for line in words_file if line.strip()]
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail={"error": {"description": "Word list not found"}},
        ) from exc

    seen_words = player.seen_words or []
    unseen_words = [word for word in words if word not in seen_words]

    if not unseen_words:
        raise HTTPException(
            status_code=422,
            detail={"error": {"description": "No words available"}},
        )

    selected_word = random.choice(unseen_words)
    player.seen_words = [*seen_words, selected_word]

    current_game = CurrentGame(secret_word=selected_word, player=player)
    game_result = GameResult(
        current_game=current_game,
        status=GameStatus.in_progress,
        word=None,
    )

    db.add(current_game)
    db.add(game_result)
    db.add(player)
    db.commit()
    db.refresh(current_game)
    return current_game


@app.get("/{id}/board")
def get_player_board(
    id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(create_database_session),
) -> PlayerBoardRead:
    token = authorization
    if token != f"Bearer {id}":
        return access_denied_response()

    existing_player = db.query(Player).filter(Player.id == id).first()

    if not existing_player:
        raise HTTPException(
            status_code=422, detail={"error": {"description": "Player not found"}}
        )

    current_game = existing_player.current_game
    if current_game is None:
        current_game = create_current_game_for_player(existing_player, db)

    return PlayerBoardRead(
        user=UserBoardRead(id=existing_player.id, name=existing_player.name),
        current=CurrentBoardRead(
            length=len(current_game.secret_word),
            guesses=[GuessRead.model_validate(guess) for guess in current_game.guesses],
            result=(
                GameResultRead.model_validate(current_game.result)
                if current_game.result is not None
                else None
            ),
        ),
    )
