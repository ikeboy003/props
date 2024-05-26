package models

type NBAPlayer struct {
	ID        string             `json:"id"`
	FullName  string             `json:"full_name"`
	FirstName string             `json:"first_name"`
	LastName  string             `json:"last_name"`
	IsActive  bool               `json:"is_active"`
	Team      string             `json:"team"`
	GameLogs  []NBAPlayerGameLog `json:"game_logs"`
}
