from dataclasses import dataclass, field
from models.nba.nbateam import NBATeam


@dataclass
class Matchup:
    homeTeam: NBATeam
    awayTeam: NBATeam
    game_time: str
