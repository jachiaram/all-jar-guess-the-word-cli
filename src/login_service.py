import sys
import httpx
import board_service
from board_service import print_board_line, print_empty_board_line
from models import GuessList
from session_service import save_player_session, load_player_session


def print_board_from_response(board_payload: dict):
    current = board_payload.get("current", {}) if isinstance(board_payload, dict) else {}
    length = current.get("length")
    guesses_payload = current.get("guesses", [])

    if not isinstance(length, int) or length <= 0:
        print("Unable to display board right now.")
        return

    try:
        guesses = GuessList.model_validate(guesses_payload).root
    except Exception:
        print("Unable to display board right now.")
        return

    if len(guesses) == 0:
        for _ in range(6):
            print_empty_board_line(length)
        return

    for guess in guesses:
        print_board_line(guess)

    for _ in range(max(0, 6 - len(guesses))):
        print_empty_board_line(length)


async def login(player_name: str):
    player_name = str.lower(player_name).strip()
    
    try:
        response = httpx.post(
            f"http://localhost:8000/players/sessions",
            json={"name": player_name},
        )
        
        if response.status_code == 200:
            player_data = response.json()
            print(f"May the odds be in your favor {player_data['name']}!\n")

            player_id = player_data.get("id")
            if isinstance(player_id, int):
                save_player_session(player_id)
                await board_service.call_board_api(load_player_session())
        elif response.status_code == 404:
            print(f"Could not find user {player_name}. Please register first with: wurdal register {player_name}")
        else:
            print(f"Failed to login player (status code: {response.status_code})")
            sys.exit(1)
    except httpx.ConnectError:
        print("Looks like the wurdal servers are taking a loss... try again later!")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)