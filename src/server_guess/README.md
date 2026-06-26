# Server Guess Module

This module implements the server-based guess flow for the Wurdal CLI game.

## Overview

The `server_guess` package handles submitting guesses to a remote server instead of using local file-based game state. It fulfills all acceptance criteria for the "submit a guess via CLI" story.

## Components

### `api_client.py`
Handles communication with the server:
- `get_player_id()` - Reads player ID from session file (`~/.wurdal_session`). Shows "Please login to continue" if missing.
- `post_guess(player_id, guess_word, server_url)` - POSTs guess to server with Bearer token auth. Handles:
  - Connection errors → "Looks like the wurdal servers are taking a loss... try again later!"
  - 400 validation errors → Prints server error message (e.g., "Guess must be exactly 5 letters")
  - Returns JSON with guesses, word_length, won, lost flags

### `guess_handler.py`
Orchestrates the full guess flow:
- Gets player ID from session
- Calls API to submit guess
- Renders the board using existing `board_service` functions
- Prints outcome: "🎉 You won! 🎉" or "Game over! The word was WORD."

### `test_api_client.py`
Unit tests covering all scenarios:
- Guess without logging in (no session file)
- Server down (connection error)
- Wrong guess length (400 from server)
- Winning guess
- Losing guess
- Correct request format (Authorization header, JSON payload)

## Usage

### Running Tests
```bash
cd /path/to/workspace/all-jar-guess-the-word-cli
pipenv run pytest src/server_guess/test_api_client.py -v
```

### Integrating into CLI

To connect this to the existing `wurdal` CLI, you would:

1. Update `utils.py` to change the `guess` command from `guess <player_name> <word>` to just `guess <word>`
2. Update `wurdal.py` to replace the local guess handler with:
   ```python
   elif args.command == "guess":
       from server_guess.guess_handler import handle_guess
       handle_guess(args.word)
   ```
3. Update `Pipfile` to add `requests` (for HTTP calls) and optionally `flask` (for testing mock server)

### Mock Server

The `mock_server.py` at the project root simulates the backend:
- Handles hardcoded test players (ID 7, 8)
- Validates guess length
- Uses the same tally-based coloring algorithm as the local game
- Auto-resets to next word after win/loss

Run it with:
```bash
pipenv run python mock_server.py
```

Then test the flow:
```bash
echo '{"player_id": "7"}' > ~/.wurdal_session
wurdal guess crane
```

## Acceptance Criteria Coverage

✅ **Successful guess with server running** - Board renders with coloring, win/loss messages  
✅ **Guess fails when server is down** - Friendly error message on connection error  
✅ **Guess fails when user not logged in** - "Please login to continue" when no session file  
✅ **Guess with wrong length** - Server sends 400, error printed  
✅ **Winning guess** - Board shows, "🎉 You won! 🎉" printed, auto-reset  
✅ **Losing guess** - Board shows, "Game over! The word was WORD." printed, auto-reset

## Notes

- This module is isolated from existing code, making it safe for parallel team development
- The mock server's `GAMES` dict can be expanded with more test players
- The session file format is simple JSON: `{"player_id": "7"}`
