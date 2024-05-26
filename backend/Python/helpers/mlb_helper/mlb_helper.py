
from client.mlb_client.mlbclient import MLBTeamsRequestClient, MLBTeamRosterRequestClient
from client.mlb_client.mlbclient import MLBPlayerGameLogClient

mlb_teams = MLBTeamsRequestClient.get_teams()

def get_player_game_log_for_season(player_id):
    player = get_player_by_id(player_id)
    if not player:
        print("Player not found")
    else:
        MLBPlayerGameLogClient.get_player_game_logs(player)
        return player.game_logs
    
def get_player_by_id(player_id: int):
    return next(
        (player for team in mlb_teams if team.roster for player in team.roster if player.id == player_id),
        None
    )