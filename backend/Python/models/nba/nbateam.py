
from models.nba.nbaplayer import NBAPlayer
from dataclasses import dataclass, field
from models.nba.defense_rank import DefensiveRanking
@dataclass
class NBATeam:
    id: str
    full_name: str
    abbreviation: str
    nickname: str
    city: str
    state: str
    defense_rank: list[DefensiveRanking] = field(default_factory=list)
    
    def set_roster(self, roster: list[NBAPlayer]):
        self.roster = roster
        
    def __post_init__(self):
        self.id = str(self.id)
    
    def has_roster(self):
        return hasattr(self, 'roster') and self.roster is not None and len(self.roster) > 0

    def set_defense_rank(self, defense_rank: DefensiveRanking):
       
        if any(dr.playerPosition == defense_rank.playerPosition for dr in self.defense_rank):
            print("already in")
        else:
            self.defense_rank.append(defense_rank)
    
    def has_defense_rank(self):
        return hasattr(self, 'defense_rank') and self.defense_rank is not None and len(self.defense_rank) > 0