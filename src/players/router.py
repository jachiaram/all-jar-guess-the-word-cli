import json
from pathlib import Path

from fastapi import APIRouter, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..core.database import create_database_session, Base

app = APIRouter()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class PlayersRegister(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str

class PlayerCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str

@app.post("", response_model=PlayerCreate, status_code=201)
def create_player(
    player: PlayersRegister,
    db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(status_code=422, detail={"error": {"description": "Name is required"}})
    
    player_name = player.name.replace(" ", "").lower()
    
    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if existing_player:
        raise HTTPException(status_code=422, detail={"error": {"description": "Name must be unique"}})

    db_player = Player(name=player_name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player


MOCK_DATA_PATH = Path(__file__).with_name("mock.json")


def access_denied_response() -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"error": {"description": "Access denied"}},
    )


def player_not_found_response(player_id: int) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"description": f"Player {player_id} not found"}},
    )


def load_mock_players() -> list[dict[str, object]]:
    with MOCK_DATA_PATH.open() as mock_file:
        return json.load(mock_file)


def find_player_board(player_id: int) -> dict[str, object] | None:
    mock_players = load_mock_players()

    for player in mock_players:
        user = player.get("user", {})
        if user.get("id") == player_id:
            return player

    return None


def normalize_current_game(player_board: dict[str, object]) -> dict[str, object]:
    current = player_board.get("current")
    if not isinstance(current, dict):
        return player_board

    result = current.get("result")
    if not isinstance(result, dict):
        return player_board

    status = result.get("status")
    if status in {"won", "lost"}:
        current["guesses"] = []
        current["result"] = {"status": "in-progress", "word": None}

    return player_board


@app.get("/{id}/board")
async def get_player_board(
    id: int,
    authorization: str | None = Header(default=None),
    authentication: str | None = Header(default=None),
) -> dict[str, object]:
    token = authorization or authentication
    if token != f"Bearer {id}":
        return access_denied_response()

    player_board = find_player_board(id)
    if player_board is None:
        return player_not_found_response(id)

    return normalize_current_game(player_board)