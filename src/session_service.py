import json
from pathlib import Path


SESSION_PATH = Path("../session.json")


def save_player_session(player_id: int):
    SESSION_PATH.write_text(
        json.dumps({"player_id": player_id}, indent=2),
        encoding="utf-8",
    )


def load_player_session() -> int | None:
    try:
        session = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

    player_id = session.get("player_id")
    if isinstance(player_id, int):
        return player_id

    return None