import time
import datetime
import redis
from nba_api.stats.endpoints import leaguedashteamstats
import json  # For converting the response to a string
from models.nba.nbateam import NBATeam  
from models.nba.defense_rank import DefensiveRanking
class DefenseHubClient:
    #192.168.1.245
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    @staticmethod
    def fetch_and_cache_defense_data(player_position: str):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cache_key = f"{player_position}:{today_str}"

        if player_position == "ALL":
            response = leaguedashteamstats.LeagueDashTeamStats(
                measure_type_detailed_defense='Opponent',
                per_mode_detailed='PerGame',
                season_type_all_star='Playoffs'
            ).league_dash_team_stats.get_dict()
        else:
            response = leaguedashteamstats.LeagueDashTeamStats(
            measure_type_detailed_defense='Opponent',
            per_mode_detailed='PerGame',
            player_position_abbreviation_nullable=player_position
        ).league_dash_team_stats.get_dict()

        # Cache the new response with an expiration time (e.g., 24 hours)
        DefenseHubClient.redis_client.set(cache_key, json.dumps(response), ex=86400)
        return response

    @staticmethod
    def get_defense_hub(team: NBATeam):
        valid_positions = ["F", "C", "G","ALL"]

        for player_position in valid_positions:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cache_key = f"{player_position}:{today_str}"

            # Try to get the cached response
            cached_response = DefenseHubClient.redis_client.get(cache_key)
            if cached_response:
                resp = json.loads(cached_response)
                DefenseHubClient.parse_response(team, resp , player_position)
            else:
                # If there's no cached response, fetch the data, cache it, and add to responses
                response = DefenseHubClient.fetch_and_cache_defense_data(player_position)
                DefenseHubClient.parse_response(team, response , player_position)
            

    @staticmethod
    def parse_response(team: NBATeam, response , player_position):

        headers = response['headers']
        data = response['data']   
        team_id_index = headers.index('TEAM_ID')
        rank_indices = {header: headers.index(header) for header in headers if 'RANK' in header}

        # Filter the data for the specified team
        team_data = next((row for row in data if row[team_id_index] == int(team.id)), None)
        if not team_data:
            print("Defense data for the specified team and position not found")
            return None

        def apply_modulo(rank):  
            teams_plus_1 = 30+1  
            return teams_plus_1-rank
        defensive_ranking = DefensiveRanking(
            playerPosition=player_position,
            oppFGA=apply_modulo(team_data[headers.index('OPP_FGA_RANK')]),
            oppFGM=apply_modulo(team_data[headers.index('OPP_FGM_RANK')]),
            opponentPointsRank=apply_modulo(team_data[rank_indices['OPP_PTS_RANK']]),
            opponentThreePointAttemptsRank=apply_modulo(team_data[rank_indices['OPP_FG3A_RANK']]),
            opponentReboundsRank=apply_modulo(team_data[rank_indices['OPP_REB_RANK']]),
            opponentAssistsRank=apply_modulo(team_data[rank_indices['OPP_AST_RANK']]),
            opponent_field_goal_percentage=apply_modulo(team_data[headers.index('OPP_FG_PCT_RANK')]),
            opponet_fg3_percentage=apply_modulo(team_data[headers.index('OPP_FG3_PCT_RANK')]),
    )

        team.set_defense_rank(defensive_ranking)

    
    @staticmethod
    def get_totals_defense(team: NBATeam):
        valid_positions = ["F", "C", "G"]

        player_position = "ALL"
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cache_key = f"{player_position}:{today_str}"

        # Try to get the cached response
        cached_response = DefenseHubClient.redis_client.get(cache_key)
        if cached_response:
            resp = json.loads(cached_response)
            DefenseHubClient.parse_response(team, resp , player_position)
        else:
            # If there's no cached response, fetch the data, cache it, and add to responses
            response = DefenseHubClient.fetch_and_cache_defense_data(player_position)
            print(response)
            DefenseHubClient.parse_response(team, response , player_position)
