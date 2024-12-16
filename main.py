import chess.pgn
import lichess.api

import json


stats = {}

def main():

    f = open('resources/analyses.json')
    data = json.load(f)

    for i in range(1, 14):
        pgn = open(f"resources/Ding-Gukesh-{i}.pgn")
        game = chess.pgn.read_game(pgn)
        json_game = lichess.api._api_get(f'/game/export/{data[str(i)]}?accuracy=true&literate=true', params={})
        print(f"WASSUP {json_game}")

        game_players = json_game["players"]
        game_white_player = game_players["white"]
        game_black_player = game_players["black"]

        initialize_structs(game_black_player, game_white_player)

        white_data = stats[game_white_player["name"]]
        black_data = stats[game_black_player["name"]]
        white_analysis = game_white_player["analysis"]
        black_analysis = game_black_player["analysis"]

        white_data["inaccuracy"] += white_analysis["inaccuracy"]
        white_data["mistake"] += white_analysis["mistake"]
        white_data["blunder"] += white_analysis["blunder"]
        white_data["acpl"] += white_analysis["acpl"]
        white_data["accuracy"] += white_analysis["accuracy"]

        black_data["inaccuracy"] += black_analysis["inaccuracy"]
        black_data["mistake"] += black_analysis["mistake"]
        black_data["blunder"] += black_analysis["blunder"]
        black_data["acpl"] += black_analysis["acpl"]
        black_data["accuracy"] += black_analysis["accuracy"]

        print('HEADERS')
        print(game.headers)
        print(game)
        curr_player = white_data
        while game.next():
            print(f"Node {game.emt()}")
            game = game.next()

    print(stats)

    def switch(data):
        if


def initialize_structs(black, white):
    white_name = white["name"]
    black_name = black["name"]
    if white_name not in stats:
        stats[white_name] = {}
        stats[white_name]["inaccuracy"] = 0
        stats[white_name]["mistake"] = 0
        stats[white_name]["blunder"] = 0
        stats[white_name]["acpl"] = 0
        stats[white_name]["accuracy"] = 0
    if black_name not in stats:
        stats[black_name] = {}
        stats[black_name]["inaccuracy"] = 0
        stats[black_name]["mistake"] = 0
        stats[black_name]["blunder"] = 0
        stats[black_name]["acpl"] = 0
        stats[black_name]["accuracy"] = 0


if __name__ == "__main__":
    main()