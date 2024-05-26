from flask import Flask, jsonify
from client.nba_client.teams_api_client import NBATeamsApiClient
from client.nba_client.player_api_client import NBAPlayerApiClient
import requests, time
from models.nba.nbateam import NBATeam
from models.nba.nbaplayer import NBAPlayer
from models.nba.matchups import Matchup
from client.nba_client.player_gamelog_client import NBAPlayerGameLogApiClient
from nba_api.stats.endpoints import commonplayerinfo
from client.nba_client.game_matchup_client import NBAGameMatchupApiClient
from typing import List
from client.nba_client.defense_client import DefenseHubClient
from models.nba.defense_rank import DefensiveRanking

nba_teams : list[NBATeam] = NBATeamsApiClient.get_teams()
active_players : list[NBAPlayer] = NBAPlayerApiClient.get_players()
def find_team_by_abbreviation(abbr):
    team = next((team for team in nba_teams if team.abbreviation == abbr), None)
    return team

def helper_get_defense_hub(team_abbreviation: str):
    team = find_team_by_abbreviation(team_abbreviation)
    if not team:
        print("Team not found")
        return None

    DefenseHubClient.get_defense_hub(team)
    return team.defense_rank

def helper_get_all_defense(Team_abbreviation: str):
    team = find_team_by_abbreviation(Team_abbreviation)
    if not team:
        print("Team not found")
        return None
    DefenseHubClient.get_totals_defense(team)
    
def helpers_get_matchups() -> List[Matchup]:
   
    resp = NBAGameMatchupApiClient.get_today_matchups()
    headers = resp['headers']  # Get the headers
    matchups_data = resp['data']  

    # Determine the indices for the relevant fields
    home_team_id_index = headers.index('HOME_TEAM_ID')
    visitor_team_id_index = headers.index('VISITOR_TEAM_ID')
    time_index = headers.index('GAME_STATUS_TEXT')

    # Initialize an empty list to store the matchups
    matchups: List[Matchup] = []

    # Iterate through the matchups data
    for game in matchups_data:
        # Use the indices to extract home and visitor team IDs
        home_team_id = game[home_team_id_index]
        visitor_team_id = game[visitor_team_id_index]
       
        # Find the corresponding NBATeam objects based on the IDs
        home_team = next((team for team in nba_teams if team.id == str(home_team_id)), None)
        away_team = next((team for team in nba_teams if team.id == str(visitor_team_id)), None)

        # Check if both teams were found
        if home_team and away_team:
            helper_get_defense_hub(home_team.abbreviation)
            helper_get_defense_hub(away_team.abbreviation)

            matchup = Matchup(homeTeam=home_team, awayTeam=away_team, game_time=game[time_index])
            matchups.append(matchup)

    return matchups

today_matchups : list[Matchup] = helpers_get_matchups()

def helpers_get_all_teams():
    return nba_teams

def helpers_get_all_active_players():
    return active_players

def helpers_get_all_teams_with_rosters():
    for team in nba_teams:
        if not hasattr(team, 'roster'):
            team = helpers_assign_team_to_roster(team, 3, 10)
            if not team or not hasattr(team, 'roster'):
                print(f"Unable to retrieve roster for team {team.abbreviation if team else 'Unknown'}.")       
    return nba_teams

def helpers_assign_team_to_roster(team_to_search: NBATeam, retries=3, delay=2):
    if not team_to_search:
        print("No team provided.")
        return None
    
    if hasattr(team_to_search, 'roster'):
        return team_to_search

    for attempt in range(retries):
        try:
            team_to_search = NBATeamsApiClient.get_and_assign_team_rosters(team_to_search, active_players)
            if hasattr(team_to_search, 'roster'):
                return team_to_search
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
    print(f"All attempts to get roster for team {team_to_search.abbreviation} failed.")
    return None

def helper_get_team_by_abbreviation(abbr):
    try:
        team = find_team_by_abbreviation(abbr)
        if not team:
            return jsonify({"error": "Team not found"}), 404

        team_with_roster = helpers_assign_team_to_roster(team, 2, 10)
        if not team_with_roster or not hasattr(team_with_roster, 'roster'):
            return jsonify({"error": "Unable to retrieve team roster"}), 404

        return jsonify(team_with_roster), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def helper_get_team_roster_by_abbreviation(abbr):
    team = find_team_by_abbreviation(abbr)    
    if not team:
        return jsonify({"error": "Team Roster was not found"}), 404
    if not hasattr(team, 'roster'):
        team = helpers_assign_team_to_roster(team, 2, 10)
        if not team or not hasattr(team, 'roster'):
            return jsonify({"error": "Team Roster was not able to be found"}), 404

    return jsonify(team.roster), 200

def helper_get_player_game_log_for_n_last_games(id, n):
    player = next((player for player in active_players if player.id == id), None)
    if not player:
        return {"error": "Player not found"}, 404

    if not hasattr(player, 'season_game_log'):
        try:
            NBAPlayerGameLogApiClient.create_player_current_season_gamelog(player)
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500

    return player.get_n_games(n), 200

def helper_get_player_current_season_log(id):
    
    player = next((player for player in active_players if player.id == id), None)
    if not player:
        return {"error": "Player not found"}, 404

        
    if not hasattr(player, 'season_game_log'):
        try:
            NBAPlayerGameLogApiClient.create_player_current_season_gamelog(player)
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500

    if len(player.season_game_log) == 0:
        return {"message": "No games logged for the current season"}, 204

    return player.season_game_log, 200

def get_player_log_df(id):
    player = next((player for player in active_players if player.id == id), None)
    if not player:
        return {"error": "Player not found"}, 404
    return NBAPlayerGameLogApiClient.get_player_df(player)


def helper_get_player_info (id):
    player = next((player for player in active_players if player.id == id), None)
    if not player:
        return {"error": "Player not found"}, 404
    player = NBAPlayerApiClient.get_player_info(player)
    return player ,200

def helper_get_player_season_or_playoff_log(player_id, season, is_playoffs=False):
    player = next((p for p in active_players if p.id == player_id), None)
    if not player:
        return {"error": "Player not found"}, 404

    try:
        gamelog = NBAPlayerGameLogApiClient.get_player_season_or_playoff_gamelog(player, season, is_playoffs)
        return gamelog, 200
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500



    

    