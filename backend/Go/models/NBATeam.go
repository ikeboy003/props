package models

type NBATeam struct {
	ID           string      `json:"id"`
	FullName     string      `json:"full_name"`
	Abbreviation string      `json:"abbreviation"`
	Nickname     string      `json:"nickname"`
	City         string      `json:"city"`
	State        string      `json:"state"`
	Roster       []NBAPlayer `json:"roster"`
}

// set roster of team
func (team *NBATeam) SetRoster(roster []NBAPlayer) {
	team.Roster = roster
}

// NewNBATeam is a constructor for NBATeam
func NewNBATeam(id, fullName, abbreviation, nickname, city, state string) *NBATeam {
	return &NBATeam{
		ID:           id,
		FullName:     fullName,
		Abbreviation: abbreviation,
		Nickname:     nickname,
		City:         city,
		State:        state,
	}
}
