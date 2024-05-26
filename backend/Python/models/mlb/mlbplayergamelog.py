from dataclasses import dataclass

@dataclass
class MLBPlayerGameLog:
    date: str
    opp: str
    ab: int
    r: int
    h: int
    tb: int
    double: int
    triple: int
    hr: int
    rbi: int
    bb: int
    ibb: int
    so: int
    sb: int
    cs: int