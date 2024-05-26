import requests
from models.mlb.mlbteam import MLBTeam
from models.mlb.mlbplayer import MLBPlayer
from models.mlb.mlbplayergamelog import MLBPlayerGameLog

class MLBTeamsRequestClient:
    @staticmethod
    def get_teams():
        url = "https://statsapi.mlb.com/api/v1/teams"
        resp = requests.get(url)
        data = resp.json()
        mlb_teams = [MLBTeam(id = team['id'], name = team['name'], teamCode = team['teamCode'], abbreviation = team['abbreviation'], locationName = team['locationName'], sport = team['sport']['name'], shortName= team['shortName'],franchiseName = team['franchiseName'], clubName = team['clubName']) for team in data['teams'] if team['sport']['name'] == "Major League Baseball" ]
        
        for team in mlb_teams:
            url = f"https://statsapi.mlb.com/api/v1/teams/{team.id}/roster"
            resp = requests.get(url)
            data = resp.json()
            roster = [MLBPlayer(id = player['person']['id'], full_name = player['person']['fullName'], jersey_number = player['jerseyNumber'], position = player['position']['name'],parent_team_id=player['parentTeamId']) for player in data['roster']]
            team.set_roster(roster)
        return mlb_teams
        
        
class MLBTeamRosterRequestClient:
    @staticmethod
    def get_team_roster(team_id):
        url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
        resp = requests.get(url)
        data = resp.json()
        roster = [MLBPlayer(id = player['person']['id'], full_name = player['person']['fullName'], jersey_number = player['jerseyNumber'], position = player['position']['name'],parent_team_id=player['parentTeamId']) for player in data['roster']]
        return roster   

class MLBPlayerGameLogClient:
    
    ## Get the Game Logs for a Player for regular season using https://statsapi.mlb.com/api/v1/people/605141/stats?stats=gameLog,statSplits,statsSingleSeason&leagueListId=mlb_hist&group=hitting&gameType=R&sitCodes=1,2,3,4,5,6,7,8,9,10,11,12&hydrate=team&season=2024&language=en
    @staticmethod
    def get_player_game_logs(player : MLBPlayer):
        url = f"https://statsapi.mlb.com/api/v1/people/{player.id}/stats?stats=gameLog,statSplits,statsSingleSeason&leagueListId=mlb_hist&group=hitting&gameType=R&sitCodes=1,2,3,4,5,6,7,8,9,10,11,12&hydrate=team&season=2024&language=en"
        resp = requests.get(url)
        if resp.status_code != 200:
            print("Error")
            return
            
        data = resp.json()
        game_logs = [
            MLBPlayerGameLog(
                date=game['date'],
                opp=game['opponent']['teamName'],
                ab=game['stat']['atBats'],
                r=game['stat']['runs'],
                h=game['stat']['hits'],
                tb=game['stat']['totalBases'],
                double=game['stat']['doubles'],
                triple=game['stat']['triples'],
                hr=game['stat']['homeRuns'],
                rbi=game['stat']['rbi'],
                bb=game['stat']['baseOnBalls'],
                ibb=game['stat']['intentionalWalks'],
                so=game['stat']['strikeOuts'],
                sb=game['stat']['stolenBases'],
                cs=game['stat']['caughtStealing']
            ) for game in data['stats'][0]['splits']
        ]
        player.set_game_logs(game_logs)