package main

import (
	"fmt"

	"props.ike/clients"
)

func main() {

	teamsClient := clients.NewNBATeamsPythonClient()

	teams, err := teamsClient.GetTeams()
	if err != nil {
		fmt.Println(err)
	}
	for _, team := range teams {
		roster, _ := teamsClient.GetRosterNames(&team)
		fmt.Println(team.FullName)
		print(roster)

	}

}
