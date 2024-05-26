package clients

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"props.ike/models"
)

const baseURL = "http://localhost:3001"

type NBAPlayerGameLogPythonClient struct {
}
type NBATeamsPythonClient struct {
}

type NBAPlayersPythonClient struct {
}

func NewNBATeamsPythonClient() *NBATeamsPythonClient {
	return &NBATeamsPythonClient{}
}

func NewNBAPlayersPythonClient() *NBAPlayersPythonClient {
	return &NBAPlayersPythonClient{}
}

func NewNBAPlayerGameLogPythonClient() *NBAPlayerGameLogPythonClient {
	return &NBAPlayerGameLogPythonClient{}
}

func (client *NBATeamsPythonClient) GetTeams() ([]models.NBATeam, error) {
	resp, err := makeRequest(baseURL + "/teams")
	if err != nil {
		return nil, err
	}

	var teams []models.NBATeam
	if err := json.Unmarshal(resp, &teams); err != nil {
		return nil, err
	}

	return teams, nil

}

func (client *NBAPlayersPythonClient) GetPlayers() ([]models.NBAPlayer, error) {
	resp, err := makeRequest(baseURL + "/players")
	if err != nil {
		return nil, err
	}

	var players []models.NBAPlayer
	if err := json.Unmarshal(resp, &players); err != nil {
		return nil, err
	}
	for _, player := range players {
		fmt.Println(player.FirstName)
	}
	return players, nil
}

// get roster of names get request to localhost:3000/teams/{abbreviation}/roster
func (client *NBATeamsPythonClient) GetRosterNames(team *models.NBATeam) ([]models.NBAPlayer, error) {

	resp, err := makeRequest(baseURL + "/team/" + team.Abbreviation + "/roster")
	if err != nil {
		return nil, err
	}

	if err := json.Unmarshal(resp, &team.Roster); err != nil {
		return nil, err
	}
	return team.Roster, nil
}

func makeRequest(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error making GET request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	return body, nil
}

// get player game logs get request to localhost:3000/roster/{id}/current
func (client *NBAPlayerGameLogPythonClient) GetPlayerGameLogs(player *models.NBAPlayer) ([]models.NBAPlayerGameLog, error) {
	resp, err := makeRequest(baseURL + "/roster/" + player.ID + "/current")
	if err != nil {
		return nil, err
	}

	if err := json.Unmarshal(resp, &player.GameLogs); err != nil {
		return nil, err
	}

	return player.GameLogs, nil
}
