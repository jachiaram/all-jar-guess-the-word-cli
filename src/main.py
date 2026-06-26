from fastapi import FastAPI
from .players.router import app as players_router

app = FastAPI()

app.include_router(players_router, prefix="/players", tags=["players"])