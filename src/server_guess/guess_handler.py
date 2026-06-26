"""
Guess handler - orchestrates the server-based guess flow.
"""

from . import api_client
from models import Guess
from board_service import print_board_line, print_empty_board_line


def handle_guess(guess_word):
    """
    Handle a guess submission via the server API.
    
    :param guess_word: the word to guess
    """
    player_id = api_client.get_player_id()
    result = api_client.post_guess(player_id, guess_word)
    
    guesses = result.get("guesses", [])
    word_length = result.get("word_length", 5)
    
    # Render the board
    for guess_data in guesses:
        g = Guess(guess=guess_data["guess"], colors=guess_data["colors"])
        print_board_line(g)
    
    # Print empty rows
    for _ in range(6 - len(guesses)):
        print_empty_board_line(word_length)
    
    # Show outcome messages
    if result.get("won"):
        print("\U0001f389 You won! \U0001f389")
    elif result.get("lost"):
        print(f"Game over! The word was {result.get('word', '').upper()}.")
