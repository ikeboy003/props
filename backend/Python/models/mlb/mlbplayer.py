from dataclasses import dataclass
from models.mlb.mlbplayergamelog import MLBPlayerGameLog
'''
create me a data class that will represent a baseball player from this response.
{'person': {'id': 642715, 'fullName': 'Willy Adames', 'link': '/api/v1/people/642715'}, 'jerseyNumber': '27', 'position': {'code': '6', 'name': 'Shortstop', 'type': 'Infielder', 'abbreviation': 'SS'}, 'status': {'code': 'A', 'description': 'Active'}, 'parentTeamId': 158}
'''

@dataclass
class MLBPlayer:
    id: int
    full_name: str
    jersey_number: str
    position: str
    parent_team_id: int
    game_logs: list[MLBPlayerGameLog] = None 
    def __post_init__(self):
        self.id = int(self.id)
        self.parent_team_id = int(self.parent_team_id)
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    def set_game_logs(self, game_logs: list[MLBPlayerGameLog]):
        self.game_logs = game_logs