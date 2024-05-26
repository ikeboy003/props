from dataclasses import dataclass, field

@dataclass
class NBAPlayerGameLog:
    player_id: str
    game_date: str
    matchup: str
    points: int
    win: str
    rebounds: int
    assists: int
    minutes: int
    fg3a: int
    fg3m: int
    stl: int
    fga: int
    fg_pct: float
    fg3_pct: float
    ft_pct: float
    fgm: int
    location: int = field(init=False)
    
    def __post_init__(self):
        self.player_id = str(self.player_id)
        self.game_date = str(self.game_date)
        self.matchup = str(self.matchup)
        self.points = int(self.points)
        self.win = str(self.win)
        self.rebounds = int(self.rebounds)
        self.assists = int(self.assists)
        self.minutes = int(self.minutes)
        self.location = 0 if "@" in self.matchup else 1
        