import time
import datetime
import redis
import json
from nba_api.stats.endpoints import scoreboardv2

class NBAGameMatchupApiClient:
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    @staticmethod
    def get_today_matchups():

        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        cache_key = f'nba_matchups:{today_str}'


        cached_data = NBAGameMatchupApiClient.redis_client.get(cache_key)
        if cached_data:
            # Deserialize the JSON data back into a Python object
            return json.loads(cached_data)
        else:
            # Make the API call if data is not in cache
            response = scoreboardv2.ScoreboardV2(day_offset=0, game_date=datetime.datetime.now()).game_header.get_dict()
            
            # Serialize the Python object to a JSON string and store in cache
            # Set an expiry time for the cache (e.g., until the end of the day)
            expire_at = datetime.datetime.now().replace(hour=23, minute=59, second=59) - datetime.datetime.now()
            NBAGameMatchupApiClient.redis_client.setex(cache_key, int(expire_at.total_seconds()), json.dumps(response))

            return response
