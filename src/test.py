import argparse
import asyncio

from board_service import call_board_api


async def main() -> int:
	parser = argparse.ArgumentParser(
		description="Run board_service.call_board_api for a player id."
	)
	parser.add_argument(
		"player_id",
		nargs="?",
		type=int,
		default=1,
		help="Player id to request from the board API (default: 1).",
	)
	args = parser.parse_args()

	try:
		result = await call_board_api(args.player_id)
	except Exception as exc:
		print(f"call_board_api failed for player {args.player_id}: {exc}")
		return 1

	print(f"call_board_api returned for player {args.player_id}: {result!r}")
	return 0


if __name__ == "__main__":
	raise SystemExit(asyncio.run(main()))


