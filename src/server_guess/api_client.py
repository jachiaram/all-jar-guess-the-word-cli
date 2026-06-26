import requests
import sys
import os
import json

SESSION_FILE = os.path.expanduser("~/.wurdal_session")


def get_player_id():
    """
    Load player_id from session file.
    
    :return: player_id string
    :raises: SystemExit(1) if not logged in
    """
    if not os.path.exists(SESSION_FILE):
        print("Please login to continue")
        sys.exit(1)
    
    with open(SESSION_FILE, 'r') as f:
        session = json.load(f)
    
    player_id = session.get('player_id')
    if not player_id:
        print("Please login to continue")
        sys.exit(1)
    
    return player_id


def save_player_id(player_id):
    """
    Save player_id to session file.
    
    :param player_id: player_id to save
    """
    with open(SESSION_FILE, 'w') as f:
        json.dump({'player_id': player_id}, f)


def post_guess(player_id, guess_word, server_url="http://localhost:8000"):
    """
    Submit a guess to the server.
    
    :param player_id: player identifier
    :param guess_word: the guessed word
    :param server_url: server endpoint
    :return: response JSON with guesses, word_length, won, lost flags
    :raises: SystemExit(1) on server error or connection failure
    """
    headers = {"Authorization": f"Bearer {player_id}"}
    payload = {"guess": guess_word}
    
    try:
        response = requests.post(
            f"{server_url}/players/{player_id}/guess",
            json=payload,
            headers=headers
        )
    except requests.exceptions.ConnectionError:
        print("Looks like the wurdal servers are taking a loss... try again later!")
        sys.exit(1)
    
    if response.status_code == 400:
        data = response.json()
        print(data.get("error", "Error: invalid guess"))
        sys.exit(1)
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        sys.exit(1)
    
    return response.json()
