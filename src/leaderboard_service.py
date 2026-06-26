from models import Player


def get_leaderboard_data(registered_players: list[Player]) -> dict:
    sorted_players = player_sort(registered_players)
    players = []
    for player in sorted_players:
        wins = player.record.wins
        average_guesses = round(player.record.guess_count / wins, 1) if wins > 0 else 0.0
        players.append({
            "name": player.name,
            "wins": wins,
            "losses": player.record.losses,
            "averageGuesses": average_guesses,
        })
    return {"players": players}


def leaderboard(registered_players: list[Player]):
    """
    Sorts the players by wins and prints the leaderboard.

    :param registered_players: a list of Player objects *
    """
    print("Leaderboard\n")
    sorted_players = player_sort(registered_players)
    if len(sorted_players) == 0:
        print("No players registered yet.")
    else:
        for i, player in enumerate(sorted_players):
            print(f"{i + 1}. {player.name} - wins: {player.record.wins}")


def player_sort(registered_players: list[Player]):
    """
    Sorts the list of Player objects by wins in descending order.

    :param registered_players: a list of Player objects *
    :returns: sorted list of Player objects 
    """
    return sorted(registered_players, key=lambda x: (-x.record.wins, x.name))