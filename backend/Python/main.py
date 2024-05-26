from flask import Flask, jsonify
from client.nba_client.teams_api_client import NBATeamsApiClient
from client.nba_client.player_api_client import NBAPlayerApiClient
from helpers.helpers import *
import requests, time
from models.nba.nbateam import NBATeam
from models.nba.nbaplayer import NBAPlayer
from client.nba_client.player_gamelog_client import NBAPlayerGameLogApiClient
from flask_cors import CORS
from helpers.mlb_helper import mlb_helper
app = Flask(__name__)
CORS(app)

@app.route('/team/<string:abbreviation>', methods=['GET'])
def get_team_by_abbr(abbreviation):
    try:
        return helper_get_team_by_abbreviation(abbreviation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nba/teams/<string:abbreviation>/roster', methods=['GET'])
def get_team_roster_by_abbr(abbreviation):
    try:
        return helper_get_team_roster_by_abbreviation(abbreviation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/players', methods=['GET'])
def get_players():
    try:
        return jsonify(helpers_get_all_active_players()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nba/teams', methods=['GET'])
def get_teams_with_roster():
    try:
        return jsonify(helpers_get_all_teams_with_rosters()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
@app.route('/nba/roster/<string:id>/<int:n>', methods=['GET'])
def get_game_log_for_n_gamees(id, n):
    try:
        result, status_code = helper_get_player_game_log_for_n_last_games(id, n)
        return jsonify(result), status_code
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/nba/roster/<string:id>/current', methods=['GET'])
def get_current_season_log( id):
    try:
        result, status_code = helper_get_player_current_season_log(id)
        return jsonify(result), status_code
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/mlb/roster/<int:id>', methods=['GET'])
def get_mlb_player(id):
    try:
        return jsonify(mlb_helper.get_player_by_id(id)),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mlb/roster/<int:id>/gamelog', methods=['GET'])
def get_mlb_player_gamelog(id):
    try:
        
        return jsonify(mlb_helper.get_player_game_log_for_season(id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def clear_all_cache():
    NBATeamsApiClient.redis_client.flushdb()

    print("All cache cleared.")

#create a path to clear the cache
@app.route('/clear_cache', methods=['GET'])
def clear_cache():
    clear_all_cache()
    try:
        clear_all_cache()
        return jsonify({"message": "Cache cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nba/roster/<string:id>/info', methods=['GET'])
def get_player_info(id):
    try:
        player,statusCode = helper_get_player_info(id)
        if statusCode == 200:
            return jsonify({
                        "first_name": player.first_name,
                        "full_name": player.full_name,
                        "id": player.id,
                        "is_active": player.is_active,
                        "last_name": player.last_name,
                        "position": player.position,
                        "seasons": player.seasons_played  # Ensure this is a list of strings
                    }), 200
        else:
            return jsonify({"error": "Player information not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/nba/matchups', methods=['GET'])
def get_matchups():
    try:       
        return jsonify(today_matchups), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nba/player/<string:id>/gamelog/<string:season>/regular', methods=['GET'])
def get_player_regular_season_log(id, season):
    result, status_code = helper_get_player_season_or_playoff_log(id, season, is_playoffs=False)
    if status_code == 200:
        return jsonify(result), 200
    else:
        return jsonify(result), status_code

@app.route('/nba/player/<string:id>/gamelog/<string:season>/playoffs', methods=['GET'])
def get_player_playoff_log(id, season):
    result, status_code = helper_get_player_season_or_playoff_log(id, season, is_playoffs=True)
    if status_code == 200:
        return jsonify(result), 200
    else:
        return jsonify(result), status_code


@app.route('/nba/defense_hub/<string:team_abbreviation>', methods=['GET'])
def get_filtered_defense_hub(team_abbreviation):
    try:
        filtered_defense_data = helper_get_defense_hub(team_abbreviation)
        if filtered_defense_data is None:
            return jsonify({"error": "No data found for the specified team and position"}), 404
        return jsonify(filtered_defense_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mlb/teams', methods=['GET'])
def get_mlb_teams():
    try:
        return jsonify(mlb_helper.mlb_teams), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mlb/teams/<string:team_abbreviation>/roster', methods=['GET'])
def get_roster_by_team_abbreviation(team_abbreviation):
    try:
        
        roster = next((team.roster for team
                       in mlb_helper.mlb_teams if team.abbreviation == team_abbreviation), None)
        if roster is None:
            return jsonify({"error": "Team not found"}), 404
        return jsonify(roster), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
clear_all_cache()
if __name__ == '__main__':
    app.run(debug=True, port=3001, host='0.0.0.0')
