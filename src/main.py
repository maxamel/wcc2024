import chess.pgn
import lichess.api

import json

import numpy as np

from src.utils import PlayerStats

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def main():

    f = open('../resources/analyses.json')
    data = json.load(f)

    stats = {}

    for i in range(1, 15):
        pgn = open(f"../resources/Ding-Gukesh-{i}.pgn")
        print(f'Processing game #{i}')
        game = chess.pgn.read_game(pgn)
        json_game = lichess.api._api_get(f'/game/export/{data[str(i)]}?accuracy=true&literate=true', params={})
        print(json_game["analysis"])

        game_players = json_game["players"]
        game_white_player = game_players["white"]
        game_black_player = game_players["black"]

        if not stats:
            stats[game_white_player["name"]] = PlayerStats(game_white_player["name"])
            stats[game_black_player["name"]] = PlayerStats(game_black_player["name"])

        white_analysis = game_white_player["analysis"]
        black_analysis = game_black_player["analysis"]

        white_stats = stats[game_white_player["name"]]
        black_stats = stats[game_black_player["name"]]

        white_stats.inaccuracy += white_analysis["inaccuracy"]
        white_stats.mistake += white_analysis["mistake"]
        white_stats.blunder += white_analysis["blunder"]
        white_stats.acpl += white_analysis["acpl"]
        white_stats.accuracy += white_analysis["accuracy"]
        white_stats.games += 1

        black_stats.inaccuracy += black_analysis["inaccuracy"]
        black_stats.mistake += black_analysis["mistake"]
        black_stats.blunder += black_analysis["blunder"]
        black_stats.acpl += black_analysis["acpl"]
        black_stats.accuracy += black_analysis["accuracy"]
        black_stats.games += 1

        print(f'The game details: \n{game.headers}')

        stats[game_white_player["name"]].move_times.append([])
        stats[game_black_player["name"]].move_times.append([])

        stats[game_white_player["name"]].clocks.append([])
        stats[game_black_player["name"]].clocks.append([])

        evals = json_game["analysis"]
        white_adv = False
        black_adv = False
        for eval in evals:
            if "eval" not in eval:
                print(f'No eval in {eval}')
                continue
            else:
                eval_val = eval["eval"]
            if not white_adv and eval_val > 100:
                white_adv = True
                stats[game_white_player["name"]].advantages += 1
                stats[game_black_player["name"]].disadvantages += 1
            elif white_adv and eval_val < 100:
                white_adv = False
                stats[game_black_player["name"]].comebacks += 1

            if not black_adv and eval_val < -100:
                black_adv = True
                stats[game_black_player["name"]].advantages += 1
                stats[game_white_player["name"]].disadvantages += 1
            elif black_adv and eval_val > -100:
                black_adv = False
                stats[game_white_player["name"]].comebacks += 1

        if "winner" in json_game:
            if json_game["winner"] == "white":
                stats[game_white_player["name"]].wins += 1
            elif json_game["winner"] == "black":
                stats[game_black_player["name"]].wins += 1

        white_prev_move = None
        black_prev_move = None
        curr_player = game_white_player
        curr_prev_move = white_prev_move
        game = game.next()
        while game:
            reversed_move = f'{str(game.move)[2:]}{str(game.move)[:2]}'
            if reversed_move == curr_prev_move:
                print(f'Player {curr_player["name"]} repeated move {game.move}')
                stats[curr_player["name"]].repeated_moves += 1
            emt = game.emt()
            if emt is None:
                print(game.clock())
                if len(stats[curr_player["name"]].clocks[-1]) == 0:
                    stats[curr_player["name"]].clocks[-1].append(7200)
                emt = stats[curr_player["name"]].clocks[-1][-1] - game.clock()
                print(f'emt is None in game {i}, clock: {game.clock()}, previous clock: {stats[curr_player["name"]].clocks[-1][-1]}, move: {game.move}. Computed move time: {emt}')
            stats[curr_player["name"]].move_times[-1].append(emt)
            stats[curr_player["name"]].clocks[-1].append(game.clock())
            # switch to other player for next move
            if curr_player["name"] == game_white_player["name"]:
                white_prev_move = str(game.move)
                curr_player = game_black_player
                curr_prev_move = black_prev_move
            else:
                black_prev_move = str(game.move)
                curr_player = game_white_player
                curr_prev_move = white_prev_move
            game = game.next()

    print(stats)

    if stats[game_black_player["name"]].advantages == 0:
        stats[game_black_player["name"]].advantages = 1
    if stats[game_white_player["name"]].advantages == 0:
        stats[game_white_player["name"]].advantages = 1
    if stats[game_black_player["name"]].disadvantages == 0:
        stats[game_black_player["name"]].disadvantages = 1
    if stats[game_white_player["name"]].disadvantages == 0:
        stats[game_white_player["name"]].disadvantages = 1

    print(f'conversion {game_white_player["name"]}: {(stats[game_white_player["name"]].wins/stats[game_white_player["name"]].advantages) * 100}')
    print(f'conversion {game_black_player["name"]}: {(stats[game_black_player["name"]].wins/stats[game_black_player["name"]].advantages) * 100}')

    print(f'comeback {game_white_player["name"]}: {(stats[game_white_player["name"]].comebacks / stats[game_white_player["name"]].disadvantages) * 100}')
    print(f'comeback {game_black_player["name"]}: {(stats[game_black_player["name"]].comebacks / stats[game_black_player["name"]].disadvantages) * 100}')

    plot_acpl(stats, game_white_player, game_black_player)
    plot_accuracy(stats, game_white_player, game_black_player)
    plot_errors(stats, game_white_player, game_black_player)
    plot_conversions(stats, game_white_player, game_black_player)
    plot_moves(stats, game_white_player, game_black_player)
    plot_repeated_moves(stats, game_white_player, game_black_player)


def plot_acpl(stats: dict[str, PlayerStats], game_white_player, game_black_player):

    white_acpl = (stats[game_white_player["name"]].acpl / stats[game_white_player["name"]].games)
    black_acpl = (stats[game_black_player["name"]].acpl / stats[game_black_player["name"]].games)

    # Sample Data
    data = {
        "Metric": ["Average Centipawn Loss"],
        game_white_player["name"]: [white_acpl],
        game_black_player["name"]: [black_acpl]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Separate into two datasets
    data_points = df.iloc[:1].melt(id_vars="Metric", var_name="Player", value_name="Rate")

    # Create subplots
    fig, axes = plt.subplots(1, 1, figsize=(12, 6), sharey=True)

    # Plot Conversion Metrics
    sns.barplot(data=data_points, x="Metric", y="Rate", hue="Player", ax=axes, palette=['red', 'green'])
    for p in axes.patches:
        axes.annotate(f'{p.get_height():.1f}',
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      fontsize=12, color='black',
                      xytext=(0, 5), textcoords='offset points')
    axes.set_title("Average Centipawn Loss")
    axes.set_ylabel("Value")
    axes.set_xlabel("Metric")

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


def plot_accuracy(stats: dict[str, PlayerStats], game_white_player, game_black_player):

    white_accuracy = (stats[game_white_player["name"]].accuracy / stats[game_white_player["name"]].games)
    black_accuracy = (stats[game_black_player["name"]].accuracy / stats[game_black_player["name"]].games)

    # Sample Data
    data = {
        "Metric": ["Accuracy"],
        game_white_player["name"]: [white_accuracy],
        game_black_player["name"]: [black_accuracy]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Separate into two datasets
    data_points = df.iloc[:1].melt(id_vars="Metric", var_name="Player", value_name="Rate")

    # Create subplots
    fig, axes = plt.subplots(1, 1, figsize=(12, 6), sharey=True)

    # Plot Conversion Metrics
    sns.barplot(data=data_points, x="Metric", y="Rate", hue="Player", ax=axes, palette=['red', 'green'])
    for p in axes.patches:
        axes.annotate(f'{p.get_height():.1f}%',
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      fontsize=12, color='black',
                      xytext=(0, 5), textcoords='offset points')
    axes.set_title("Average Accuracy")
    axes.set_ylabel("Percentage")
    axes.set_xlabel("Metric")

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


def plot_errors(stats: dict[str, PlayerStats], game_white_player, game_black_player):
    white_inaccuracy = stats[game_white_player["name"]].inaccuracy
    black_inaccuracy = stats[game_black_player["name"]].inaccuracy

    white_mistake = stats[game_white_player["name"]].mistake
    black_mistake = stats[game_black_player["name"]].mistake

    white_blunder = stats[game_white_player["name"]].blunder
    black_blunder = stats[game_black_player["name"]].blunder

    # Sample Data
    data = {
        "Metric": ["Inaccuracy", "Mistake", "Blunder"],
        game_white_player["name"]: [white_inaccuracy, white_mistake, white_blunder],
        game_black_player["name"]: [black_inaccuracy, black_mistake, black_blunder]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Separate into two datasets
    data_points = df.iloc[:3].melt(id_vars="Metric", var_name="Player", value_name="Count")

    # Create subplots
    fig, axes = plt.subplots(1, 1, figsize=(18, 6), sharey=True)

    # Plot Conversion Metrics
    sns.barplot(data=data_points, x="Metric", y="Count", hue="Player", ax=axes, palette=['red', 'green'])
    for p in axes.patches:
        axes.annotate(f'{p.get_height():.1f}',
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      fontsize=12, color='black',
                      xytext=(0, 5), textcoords='offset points')
    axes.set_title("Errors")
    axes.set_ylabel("Amount")
    axes.set_xlabel("Metric")

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


def plot_conversions(stats: dict[str, PlayerStats], game_white_player, game_black_player):

    white_conversion = (stats[game_white_player["name"]].wins / stats[game_white_player["name"]].advantages) * 100
    black_conversion = (stats[game_black_player["name"]].wins / stats[game_black_player["name"]].advantages) * 100

    white_comeback = (stats[game_white_player["name"]].comebacks / stats[game_white_player["name"]].disadvantages) * 100
    black_comeback = (stats[game_black_player["name"]].comebacks / stats[game_black_player["name"]].disadvantages) * 100

    # Sample Data
    data = {
        "Metric": ["Conversion", "Comeback"],
        game_white_player["name"]: [white_conversion, white_comeback],
        game_black_player["name"]: [black_conversion, black_comeback]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Separate into two datasets
    data_points = df.iloc[:2].melt(id_vars="Metric", var_name="Player", value_name="Rate")

    # Create subplots
    fig, axes = plt.subplots(1, 1, figsize=(12, 6), sharey=True)

    # Plot Conversion Metrics
    sns.barplot(data=data_points, x="Metric", y="Rate", hue="Player", ax=axes, palette=['red', 'green'])
    for p in axes.patches:
        axes.annotate(f'{p.get_height():.1f}%',
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      fontsize=12, color='black',
                      xytext=(0, 5), textcoords='offset points')
    axes.set_title("Resilience and Consistency")
    axes.set_ylabel("Rate")
    axes.set_xlabel("Metric")

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


def plot_moves(stats: dict[str, PlayerStats], game_white_player, game_black_player):
    list1 = list(stats[game_white_player["name"]].mean_move_times_list())[:10]
    list2 = list(stats[game_black_player["name"]].mean_move_times_list())[:10]

    max_length = max(len(list1), len(list2))
    list1 = list1 + [np.nan] * (max_length - len(list1))
    list2 = list2 + [np.nan] * (max_length - len(list2))
    # Combine the data into a DataFrame
    data = pd.DataFrame({
        'Index': list(range(max_length)) * 2,
        'Value': list1 + list2,
        'List': [game_white_player["name"]] * max_length + [game_black_player["name"]] * max_length
    })
    sns.lineplot(data=data, x='Index', y='Value', hue='List', palette=['red', 'green'])
    plt.title("Move Time Comparison")
    plt.xlabel("Move Number")
    plt.ylabel("Move Time")
    plt.legend(title='Players')
    plt.show()


def plot_repeated_moves(stats: dict[str, PlayerStats], game_white_player, game_black_player):

    white_accuracy = (stats[game_white_player["name"]].repeated_moves)
    black_accuracy = (stats[game_black_player["name"]].repeated_moves)

    # Sample Data
    data = {
        "Metric": ["Repeated Moves"],
        game_white_player["name"]: [white_accuracy],
        game_black_player["name"]: [black_accuracy]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Separate into two datasets
    data_points = df.iloc[:1].melt(id_vars="Metric", var_name="Player", value_name="Rate")

    # Create subplots
    fig, axes = plt.subplots(1, 1, figsize=(12, 6), sharey=True)

    # Plot Conversion Metrics
    sns.barplot(data=data_points, x="Metric", y="Rate", hue="Player", ax=axes, palette=['red', 'green'])
    for p in axes.patches:
        axes.annotate(f'{p.get_height():.1f}',
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      fontsize=12, color='black',
                      xytext=(0, 5), textcoords='offset points')
    axes.set_title("Repeated Moves")
    axes.set_ylabel("Amount")
    axes.set_xlabel("Metric")

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
