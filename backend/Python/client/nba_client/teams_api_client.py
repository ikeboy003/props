from models.nba.nbaplayer import NBAPlayer
from models.nba.nbateam import NBATeam
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
import redis ,json


class NBATeamsApiClient:  
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)  

    @staticmethod
    def get_teams():
        return [NBATeam(team['id'], team['full_name'], team['abbreviation'], team['nickname'], team['city'], team['state']) for team in teams.get_teams()]
    
    ##API Call to Get the Roster
    @staticmethod
    def assign_roster(team : NBATeam, active_players : list[NBAPlayer]):          
        response = commonteamroster.CommonTeamRoster(team.id).get_dict()
        team_roster_string =  NBATeamsApiClient.process_roster_response(response)
        print(team_roster_string)
        filtered_team = [player for player in active_players if player.full_name in team_roster_string]
        team = NBATeamsApiClient.set_roster(team,filtered_team)
        
    @staticmethod
    def process_roster_response(response):
        team_roster = next((item for item in response['resultSets'] if item['name'] == 'CommonTeamRoster' and 'rowSet' in item and item['rowSet']), None)
        return [row[team_roster['headers'].index('PLAYER')] for row in team_roster['rowSet']] if team_roster else []
    
    @staticmethod
    def set_roster(team : NBATeam, filtered_team : list[NBAPlayer]):
        team.set_roster(filtered_team)
                
    @staticmethod
    def get_team_roster(team: NBATeam):
        
        cached_roster = NBATeamsApiClient.redis_client.get(f"team_roster_{team.id}")
        if cached_roster:
            print(f"Cache Hit!: Getting Team Roster for {team.full_name} from Cache")           
            return json.loads(cached_roster)
        print(f"Getting Team Roster {team.full_name}from API") 
        response = commonteamroster.CommonTeamRoster(team.id).get_dict()
        if not response or 'resultSets' not in response:
            return []

        team_roster = next((item for item in response['resultSets'] if item['name'] == 'CommonTeamRoster' and 'rowSet' in item), None)
        roster = [row[team_roster['headers'].index('PLAYER')] for row in team_roster['rowSet']] if team_roster else []

        if roster:
            NBATeamsApiClient.redis_client.setex(f"team_roster_{team.id}", 3600, json.dumps(roster))  # Cache for 1 hour
        return roster
   
    @staticmethod
    def get_and_assign_team_rosters(team: NBATeam, active_players: list[NBAPlayer]):
        if not team or not isinstance(team, NBATeam) or not active_players:
            return None
        roster = NBATeamsApiClient.get_team_roster(team)
        if not roster:
            return team

        filtered_roster = [player for player in active_players if player.full_name in roster]
        NBATeamsApiClient.set_roster(team, filtered_roster)
        return team


    