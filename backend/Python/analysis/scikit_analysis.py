from helpers.helpers import *
import pandas as pd
from nba_api.stats.endpoints import playergamelog


def get_player_game_log_for_season(player_id):
    player = next((player for player in active_players if player.id == player_id), None)
    if not player:
        print("Player not found")
    
    player_game_log = playergamelog.PlayerGameLog(player_id=player.id,season="2023").get_data_frames()
    print(player_game_log)

  

