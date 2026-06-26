from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Load word list from file
def load_word_pool():
    word_list_path = os.path.join(os.path.dirname(__file__), 'src', 'word_list.txt')
    with open(word_list_path, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    return words

WORD_POOL = load_word_pool()

# Initialize games with words from the pool
GAMES = {
    "7": {"word": WORD_POOL[0] if WORD_POOL else "crane", "guesses": [], "word_pool_index": 0},
    "8": {"word": WORD_POOL[1] if len(WORD_POOL) > 1 else "stole", "guesses": [], "word_pool_index": 1},
}


def _color_guess(guess: str, secret_word: str) -> dict:
    """Colors a guess using the same tally-based algorithm as guess_service."""
    tally = {}
    for c in secret_word:
        tally[c] = tally.get(c, 0) + 1

    colors = {}
    # First pass: greens
    for i, char in enumerate(guess):
        if char == secret_word[i]:
            colors[str(i)] = "green"
            tally[char] -= 1

    # Second pass: yellows and greys
    for i, char in enumerate(guess):
        if str(i) not in colors:
            if char in secret_word and tally.get(char, 0) > 0:
                colors[str(i)] = "yellow"
                tally[char] -= 1
            else:
                colors[str(i)] = "grey"

    return colors


@app.route('/players/<player_id>/guess', methods=['POST'])
def make_guess(player_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {player_id}':
        return jsonify({"error": "Unauthorized"}), 401

    # Auto-create game for new player_id
    if player_id not in GAMES:
        GAMES[player_id] = {"word": WORD_POOL[0], "guesses": [], "word_pool_index": 0}

    data = request.get_json()
    guess = data.get('guess', '').lower()
    game = GAMES[player_id]
    secret_word = game['word']

    if len(guess) != len(secret_word):
        return jsonify({"error": f"Guess must be exactly {len(secret_word)} letters"}), 400

    if not guess.isalpha():
        return jsonify({"error": "Guess must contain only letters"}), 400

    colors = _color_guess(guess, secret_word)
    game['guesses'].append({"guess": guess, "colors": colors})

    won = guess == secret_word
    lost = not won and len(game['guesses']) >= 6

    response_data = {
        "guesses": list(game['guesses']),
        "word_length": len(secret_word),
        "won": won,
        "lost": lost,
    }

    if lost:
        response_data["word"] = secret_word

    if won or lost:
        pool_idx = (game.get('word_pool_index', 0) + 1) % len(WORD_POOL)
        game['word'] = WORD_POOL[pool_idx]
        game['word_pool_index'] = pool_idx
        game['guesses'] = []

    return jsonify(response_data), 200


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=False)
