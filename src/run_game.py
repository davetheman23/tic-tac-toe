#!/usr/bin/env python

import threading
import time

from src.algorithm.learning_agents import Mode
from view.visualizer import Visualizer
from model.player import RandomPlayer, HumanPlayer, MinimaxPlayer, MCPlayer, PlayerType
from model.game import Game

NUM_BOARD_ROWS = 3
NUM_BOARD_COLS = 3
NUM_CONNECTS_TO_WIN = 3


def play_non_stop(game, max_num_games, learn=False):
    games_played = 0
    while games_played < max_num_games:
        game.play()
        games_played += 1
        print("========== Finished Game # {} ===========".format(games_played))
        # with open("results.txt", "{}".format("w" if games_played == 1 else "a")) as f:
        #     f.write("game #: {} winner: {}\n".format(games_played, game.get_winner() or "draw"))
        if learn is False:
            time.sleep(0.1)
        game.reset()


def start_game(players, max_num_games, is_learning):
    g = Game(players, NUM_BOARD_ROWS, NUM_BOARD_COLS, NUM_CONNECTS_TO_WIN)
    g.learning = is_learning
    for player in players:
        if hasattr(player, "set_mode"):
            player.set_mode(Mode.Learn if is_learning else Mode.Play)
        player.set_game(g)
    t = threading.Thread(target=play_non_stop, kwargs={'game': g, 'max_num_games': max_num_games, 'learn': is_learning})
    t.daemon = True
    t.start()
    if is_learning:
        t.join()
    return g


def main():
    print("Initializing game with players...")
    minimax_player = MinimaxPlayer("MiniMax Player", PlayerType.MaxPlayer, to_start=True)
    human_player = HumanPlayer("Human Player", PlayerType.MaxPlayer)
    mc_player1 = MCPlayer("MC Player 1", PlayerType.MaxPlayer)
    mc_player2 = MCPlayer("MC Player 2", PlayerType.MinPlayer)

    print("Let the players to learn first")
    start_game(players=[mc_player1, mc_player2], max_num_games=100000, is_learning=True)

    print("Now let's play!!!")
    g = start_game(players=[human_player, mc_player2], max_num_games=100, is_learning=False)

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(g)
    vis.run()


if __name__ == '__main__':
    main()
