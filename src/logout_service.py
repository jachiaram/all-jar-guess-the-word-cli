from session_service import save_player_session, load_player_session

async def logout():
    player_id = load_player_session()
    if player_id is None:
        print("No player is currently logged in.")
        return

    print("You have been logged out successfully.")
    save_player_session(None)