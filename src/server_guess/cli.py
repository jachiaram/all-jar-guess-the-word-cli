#!/usr/bin/env python
import sys
import os

# Add src directory to path so imports work
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_dir)

from server_guess.guess_handler import handle_guess

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: wurdal guess <word>")
        sys.exit(2)
    handle_guess(sys.argv[1])
