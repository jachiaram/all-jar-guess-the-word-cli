import sys
import argparse
import random
import re
from pydantic import BaseModel, TypeAdapter, ValidationError

class Word(BaseModel):
    word: str 
    result: str | None = None 
    guesses: list[str]

class Record(BaseModel):
    wins: int
    guess_count: int

class Player(BaseModel):
    name: str
    current_word_index: int
    current_word: Word | None = None
    game_in_progress: bool
    seen_words: list[Word]
    record: Record

word_list = ["hush", "harden", "slant", "lashed", "whirr", "online", "thorn", "wearer", "soled", "award", "sward", "sane", "slide", "watt", "estate", "lender", "hone", "strewn", "shone", "inhale", "sadist", "sewed", "tow", "whined", "swath", "aslant", "hoed", "astern", "salt", "hoist", "dilute", "dared", "dud", "hearse", "silent", "unseat", "rostra", "soot", "seethe", "whirl", "rioted", "riddle", "tented", "hand", "unsaid", "unseen", "audit", "waddle", "unread", "hereto", "learnt", "stern", "weird", "died", "horded", "hint", "shat", "tittle", "show", "tinier", "adore", "risen", "when", "woolen", "lute", "indue", "direst", "aster", "erased", "stole", "then", "worth", "shut", "raster", "swear", "dense", "rid", "artier", "taint", "dare", "worsen", "aloud", "stow", "salad", "oleo", "senate", "dill", "other", "loiter", "roil", "sassed", "resale", "stein", "tread", "wheel", "reset", "wen", "wear", "hooted", "wine", "redone", "deal", "rash", "ewe", "dent", "dialed", "ended", "insert", "turret", "listen", "herein", "deed", "lesson", "rider", "load", "rhea", "shout", "well", "rodeo", "outed", "retard", "nodded", "eroded", "waste", "dried", "adorn", "thwart", "sort", "wonted", "uh"]

class WurdalArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")

def parse_args():
    parser = WurdalArgumentParser(prog='wurdal', description='Wordle Cli')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # wurdal register <player-name>
    register_parser = subparsers.add_parser('register', help='Register a new player')
    register_parser.add_argument('player_name', metavar='player-name')

    # wurdal new-game <player-name>
    new_game_parser = subparsers.add_parser('new-game', help='Start a new game')
    new_game_parser.add_argument('player_name', metavar='player-name')

    # wurdal guess <player-name> <word>
    guess_parser = subparsers.add_parser('guess', help='Make a guess')
    guess_parser.add_argument('player_name', metavar='player-name')
    guess_parser.add_argument('word')

    # wurdal leaderboard [--by-games]
    leaderboard_parser = subparsers.add_parser('leaderboard', help='Show leaderboard')
    leaderboard_parser.add_argument('--by-games', action='store_true', help='Sort by number of games played')

    return parser.parse_args()

def load_players():
    try:
        json_data = '' 
        with open('players.json', 'r', encoding='utf-8') as f:
            json_data = f.read()
        return TypeAdapter(list[Player]).validate_json(json_data)     
    except FileNotFoundError:
        print("Error: File Not Found")
    except ValidationError as e:
        print("Error: Invalid Json") 

def write_players(registered_players):
    try:
        adapter = TypeAdapter(list[Player])
        json_bytes = adapter.dump_json(registered_players)
        with open('players.json', 'wb') as f:
            f.write(json_bytes)
    except FileNotFoundError:
        print("Error: File Not Found")

def main():
    registered_players = load_players()    
    args = parse_args()

    if args.command == 'register':
        print('register')
        register(args.player_name, registered_players)
    elif args.command == 'new-game':
        print('new-game')
        new_game(args.player_name, registered_players)
    elif args.command == 'guess':
        print('guess')
        guess(args.player_name, args.word, registered_players)
    elif args.command == 'leaderboard':
        print('leaderboard')
        leaderboard(registered_players)

    write_players(registered_players)

def register(player_name, registered_players):
    # if player name is empty
    if player_name == "":
        print("Error: Blank player name provided.")
        sys.exit(1)

    # if player already exists
    if any(player.name == player_name for player in registered_players):
        print("Error: Player already registered.")
        sys.exit(1) 

    # if player name does not contain only letters, numbers, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    if (re.match(pattern, player_name)) == False:
        print("Error: Invalid player name provided.")
        sys.exit(1)
    
    player = Player(name=player_name, current_word_index=-1, seen_words=[], game_in_progress=False, record=Record(wins=0, guess_count=0))
    registered_players.append(player)

def new_game(player_name, registered_players):
    
    # if player is not registered
    if player_name not in registered_players:
        print("Error: Player not found")
        sys.exit(1)
    
    player = registered_players[registered_players.index(player_name)]
    
    # if player is already in a game
    if player.game_in_progress == True:
        print("Error: Game in progress")
        sys.exit(1) 

    # if player has seen all the words
    if len(player.seen_words) == len(word_list): ################# change if we're using full list of words
        print("Error: No more words available")
        sys.exit(1)

    select_word(player)
    print_board(player)
    player.game_in_progress = True

def select_word(player):
    # pick a random word from the word list that the player has not seen before
    idx = random.randint(0, len(word_list) - 1)
    word = word_list[idx]

    while word in player.seen_words:
        idx = random.randint(0, len(word_list) - 1)
        word = word_list[idx]

def guess(player, guess, registered_players):
    # if game has not started yet
    if player.game_in_progress == False:
        print("Error: No active game")
        sys.exit(1)

    word = player.current_word.word

    # guess validation
    guess_validation(guess, word)

    if guess == word:
        player.record.wins += 1
        player.record.guess_count += len(player.current_guesses)
    # track guesses after loss
    elif len(player.current_guesses) == 6:
        player.record.guess_count += 6 

    grey = []
    yellow = []
    yellow_idx = []
    green = []
    # check if in word (set to yellow)

    # check one to one positions for green
    # if green -1 for dict count
    # second iteration for yellow - if in dict and not in green and count > 0 add yellow and yellow idx, else add grey

    for i, c in enumerate(guess):
        if c in player.current_word.word:
            # dict check
            # if in dict check count
                # if count == 0 
                    # add grey
                    # online
                    # xxxxee
                # else add yellow and yellow idx
            yellow.append(c)
            yellow_idx.append(i)
        else:
            grey.append(c)

    # check if in position (set to green)
    for idx in yellow_idx:
        if guess[idx] == player.current_word.word[idx]:
            green.append(guess[idx])
            yellow.remove(guess[idx])
    
def guess_validation(guess, word):
    # checks the length of the guess
    if guess < len(word) or guess > len(word):
        print("Error: Invalid guess")
        sys.exit(1)
    
    # checks if the guess is all letters
    if guess.isalpha() == False:
        print("Error: Invalid guess")
        sys.exit(1)

def print_board(player):
    # if game has not started yet
    if player.game_in_progress == False:
        print("Error: No active game")
        sys.exit(1)
        

    # if player has not made any guesses yet, print empty board
    if player.current_guesses == []:
        for i in range(6):
            print_empty_board_line()
    else:
        # print game with guesses
        for guess in player.current_guesses:
            print_board_line(guess)

        for i in range(6 - len(player.current_guesses)):
            print_empty_board_line()

def print_empty_board_line():
    print("*****  *****  *****  *****  *****")
    print("*   *  *   *  *   *  *   *  *   *")
    print("*****  *****  *****  *****  *****")

def print_board_line(guess):
    print("*****  *****  *****  *****  *****")
    
    guess_line = ""
    for c in guess.word:
        guess_line += "* " + c + " *  "
    print(guess_line)

    print("*****  *****  *****  *****  *****")


def leaderboard(registered_players):
    sorted_players = player_sort(registered_players)
    for i, player in enumerate(registered_players):
        print(f"{i + 1}. {player.name} - Wins: {player.record.wins}, Guesses: {player.record.losses}")

def player_sort(registered_players):
    least_guesses = min(player.record.guess_count for player in registered_players)

if __name__ == "__main__":
    main()