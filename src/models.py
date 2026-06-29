from pydantic import BaseModel, RootModel


class Letter(BaseModel):
    letter: str
    match: str


class Guess(BaseModel):
    letters: list[Letter]


class GuessList(RootModel[list[Guess]]):
    pass


class Word(BaseModel):
    word: str
    guesses: list[Guess]


class Record(BaseModel):
    wins: int
    losses: int = 0
    guess_count: int


class Player(BaseModel):
    name: str
    current_word_index: int
    current_word: Word | None = None
    game_in_progress: bool
    seen_words: list[Word]
    record: Record
