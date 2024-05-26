import time
import json
import redis
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from models.nba.nbaplayergamelog import NBAPlayerGameLog
from models.nba.nbaplayer import NBAPlayer

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class NBAPlayerGameLogApiClient:
    @staticmethod
    def create_player_current_season_gamelog(player: NBAPlayer):
        current_season = "current_season"
        cache_key = f"player_gamelog:{player.id}:{current_season}"
        
        cached_data = redis_client.get(cache_key)
        if cached_data:         
            print("Cache Hit!: Getting Player Stats from Cache")
            response = json.loads(cached_data)
        else:
            print("Getting Player Stats from NBA API")
            max_retries = 3
            retry_delay = 2  # seconds
            retries = 0
            while retries < max_retries:
                try:
                    response = playergamelog.PlayerGameLog(player_id=player.id).get_dict()
                    redis_client.set(cache_key, json.dumps(response), ex=86400)  # Cache with TTL
                    break
                except Exception as e:
                    print(f"Request failed with error {e}, retrying...")
                    time.sleep(retry_delay)
                    retries += 1
                    if retries == max_retries:
                        raise Exception("Max retries reached, unable to fetch player game log.")
        
        gamelog = NBAPlayerGameLogApiClient._parse_response_to_gamelogs(player.id, response)        
        player.set_season_game_log(gamelog)
        return player.season_game_log
    
    @staticmethod
    def _parse_response_to_gamelogs(player_id, response):
        headers = response['resultSets'][0]['headers']
        games = response['resultSets'][0]['rowSet']
        
        # Convert each game entry using map_game_to_log
        gamelog = [NBAPlayerGameLogApiClient.map_game_to_log(player_id, game, headers) for game in games]
        return gamelog
    
    @staticmethod
    def map_game_to_log(player_id, game, headers):
        return NBAPlayerGameLog(
            player_id, 
            game[headers.index('GAME_DATE')], 
            game[headers.index('MATCHUP')],
            game[headers.index('PTS')],
            game[headers.index('WL')],
            game[headers.index('REB')],
            game[headers.index('AST')],
            game[headers.index('MIN')],
            game[headers.index('FG3A')],
            game[headers.index('FG3M')],
            game[headers.index('STL')],
            game[headers.index('FGA')],
            game[headers.index('FG_PCT')],
            game[headers.index('FG3_PCT')],
            game[headers.index('FT_PCT')],
            game[headers.index('FGM')]
        )
    
    @staticmethod
    def get_player_df(player: NBAPlayer):
        data_frames = playergamelog.PlayerGameLog(player_id=player.id).get_data_frames()
        return data_frames[0]

    @staticmethod
    def get_player_season_or_playoff_gamelog(player: NBAPlayer, season: str, is_playoffs: bool = False):
        season_type = "Playoffs" if is_playoffs else "Regular Season"
        cache_key = f"player_gamelog:{player.id}:{season}:{'playoffs' if is_playoffs else 'regular'}"
        
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Cache Hit!: Getting Player Stats from Cache")
            response = json.loads(cached_data)
        else:
            print(f"Getting Player Stats from NBA API for {season} {season_type}")
            max_retries = 3
            retry_delay = 2  # seconds
            retries = 0
            while retries < max_retries:
                try:
                    response = playergamelog.PlayerGameLog(player_id=player.id, season=season, season_type_all_star=season_type).get_dict()
                    redis_client.set(cache_key, json.dumps(response), ex=86400)  # Cache with TTL
                    break
                except Exception as e:
                    print(f"Request failed with error {e}, retrying...")
                    time.sleep(retry_delay)
                    retries += 1
                    if retries == max_retries:
                        raise Exception("Max retries reached, unable to fetch player game log.")
        
        gamelog = NBAPlayerGameLogApiClient._parse_response_to_gamelogs(player.id, response)
        return gamelog