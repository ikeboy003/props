from dataclasses import dataclass  
from models.mlb.mlbplayer import MLBPlayer
#write me a class that will represent a baseball team from this response.
'''
   ",
   "id":108,
   "name":"Los Angeles Angels",
   "teamCode":"ana",
   "fileCode":"ana",
   "abbreviation":"LAA",
   "teamName":"Angels",
   "locationName":"Anaheim",
   "sport":{
      "name":"Major League Baseball"
   },
   "shortName":"LA Angels",
   "franchiseName":"Los Angeles",
   "clubName":"Angels",
'''
@dataclass
class MLBTeam:
    id: int
    name: str
    teamCode: str
    abbreviation: str
    locationName: str
    sport: dict
    shortName: str
    franchiseName: str
    clubName: str
    roster: list[MLBPlayer] = None
    def __post_init__(self):
        self.id = int(self.id)
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    def set_roster(self, roster: list[MLBPlayer]):
        self.roster = roster