/*
create me a struct that will hold the data for the NBAPlayerGameLog

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
*/
package models

type NBAPlayerGameLog struct {
	PlayerID string `json:"player_id"`
	GameDate string `json:"game_date"`
	Matchup  string `json:"matchup"`
	Points   int    `json:"points"`
	Win      string `json:"win"`
	Rebounds int    `json:"rebounds"`
	Assists  int    `json:"assists"`
	Minutes  int    `json:"minutes"`
}
