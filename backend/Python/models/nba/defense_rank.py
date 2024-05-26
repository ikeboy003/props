from dataclasses import dataclass, field

@dataclass
class DefensiveRanking:
    playerPosition: str
    oppFGA: int
    oppFGM: int
    opponentPointsRank: float
    opponentThreePointAttemptsRank: int
    opponentAssistsRank: int
    opponentReboundsRank: int
    opponent_field_goal_percentage: float
    opponet_fg3_percentage: float
    

