
from dataclasses import dataclass, field
from models.nba.nbaplayergamelog import NBAPlayerGameLog
@dataclass
class NBAPlayer:
    id: str 
    full_name: str
    first_name: str
    last_name: str
    is_active: bool
    team: str = None  
    position: str = None
    def set_season_game_log(self, game_log: list[NBAPlayerGameLog]):
        self.season_game_log = game_log
        
    def __post_init__(self):
        self.id = str(self.id)
    
    def get_n_games(self, n):
        return self.season_game_log[:n]
    
    def set_team(self, team_name: str, team_id: str):
        self.team = team_name
        
    def has_team(self):
        return hasattr(self, 'team') and self.team is not None
    
    def set_player_position(self, position: str):
        self.position = position
    
    def set_player_info(self, team_name: str, team_id: str, position: str):
        self.set_team(team_name, team_id)
        self.set_player_position(position)
    
    def set_seasons_played(self, seasons_played: list[str]):
        self.seasons_played = seasons_played