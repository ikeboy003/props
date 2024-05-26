from nba_api.stats.static import players
from models.nba.nbaplayer import NBAPlayer
from concurrent.futures import ThreadPoolExecutor
from nba_api.stats.endpoints import commonplayerinfo
import redis ,json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class NBAPlayerApiClient:

    @staticmethod
    def create_player(player_data):
        return NBAPlayer(player_data['id'], player_data['full_name'], player_data['first_name'], player_data['last_name'], player_data['is_active'])

    @staticmethod
    def get_players():
        
        nba_players = players.get_active_players()
        with ThreadPoolExecutor() as executor:
            players_list = list(executor.map(NBAPlayerApiClient.create_player, nba_players))
        return players_list
    
    @staticmethod
    def get_player_info(player: NBAPlayer):
        player_info_key = f"player_info:{player.id}"
        player_available_seasons_key = f"player_seasons:{player.id}"
        
        # Attempt to retrieve cached player info and seasons
        cached_player_info = redis_client.get(player_info_key)
        cached_player_seasons = redis_client.get(player_available_seasons_key)
        
        if cached_player_info and cached_player_seasons:
            player_info_dict = json.loads(cached_player_info)
            player_seasons_dict = json.loads(cached_player_seasons)
            print("Returning cached data")
        else:
            # Fetch data from the NBA API
            player_info_response = commonplayerinfo.CommonPlayerInfo(player_id=player.id)
            player_info_dict = player_info_response.common_player_info.get_dict()
            player_seasons_dict = player_info_response.available_seasons.get_dict()
            
            # Cache the fetched data
            redis_client.set(player_info_key, json.dumps(player_info_dict), ex=86400)  # 24 hours expiration
            redis_client.set(player_available_seasons_key, json.dumps(player_seasons_dict), ex=86400)
            print("Data fetched from API and cached")
 
        # Extract the desired information from player_info_dict
        if 'data' in player_info_dict and 'data' in player_seasons_dict and player_info_dict['data'] and player_seasons_dict['data']:
            infoHeaders = player_info_dict['headers']
            infoData = player_info_dict['data'][0]
            seasonData = player_seasons_dict['data']
            seasonData = [season[0] for season in seasonData]
            player.set_player_position(infoData[infoHeaders.index('POSITION')])   
            player.set_seasons_played(seasonData)
            return player
        else:
            print(f"Unable to retrieve player info for {player.full_name}")
            return {"error": "Player information not found"}
                
            