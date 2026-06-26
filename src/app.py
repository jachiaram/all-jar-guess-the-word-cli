import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from leaderboard_service import get_leaderboard_data
from utils import load_players


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/leaderboard":
            players = load_players()
            data = get_leaderboard_data(players)
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def run(port=8080):
    server = HTTPServer(("", port), RequestHandler)
    print(f"Listening on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
