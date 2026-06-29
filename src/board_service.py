import sys
from models import Guess, GuessList
from httpx import AsyncClient


async def call_board_api(player_id: int | None):
    if player_id is None:
        print("Please login to continue")
        sys.exit(2)

    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/players/{player_id}/board",
                headers={"Authorization": f"Bearer {player_id}"},
            )
        player = response.json()
        print(player)
        guesses = GuessList.model_validate(player["current"]["guesses"]).root

        if len(guesses) == 0:
            for i in range(6):
                print_empty_board_line(player["current"]["length"])
        else:
            for guess in guesses:
                print_board_line(guess)

            for i in range(6 - len(guesses)):
                print_empty_board_line(player["current"]["length"])
    except ConnectionError:
        print("Looks like the wurdal servers are taking a loss... try again later!")
        sys.exit(2)


def print_empty_board_line(count: int):
    """
    Prints an empty line of the game board.

    :param count: an int for the number of tile spaces to print *
    """
    line = ""
    spaces = ""
    for i in range(count):
        line += "*****  "
        spaces += "*   *  "
    print(line)
    print(spaces)
    print(line)


def print_color(color: str, to_print: str):
    """
    Matches the given color to the ANSI color code and returns the string
    with the color code.

    :param color: color for the given string *
    :param to_print: string to be printed *
    :returns: string with ANSI color codes for the given color and text
    """
    match color:
        case "green":
            return f"\033[32m{to_print}\033[32m\033[0m"
        case "yellow":
            return f"\033[33m{to_print}\033[33m\033[0m"
        case "grey":
            return f"\033[37m{to_print}\033[37m\033[0m"
        case _:
            print("Error: internal error")
            exit(3)


def print_board_line(guess: Guess):
    """
    Prints a line of the game board.

    :param guess: a Guess object *
    """
    match_to_color = {
        "full": "green",
        "partial": "yellow",
        "none": "grey",
    }

    line = ""

    for letter in guess.letters:
        color = match_to_color.get(letter.match, "grey")
        line += print_color(color, "*****  ")

    print(line)
    guess_line = ""
    for letter in guess.letters:
        color = match_to_color.get(letter.match, "grey")
        guess_line += print_color(color, "* ")
        guess_line += letter.letter
        guess_line += print_color(color, " *  ")
    print(guess_line)
    print(line)
