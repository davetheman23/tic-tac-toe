#!/usr/bin/env python

import threading
import time

from view.visualizer import Visualizer
from model.player import RandomPlayer, HumanPlayer, MinimaxPlayer, PlayerType
from model.game import Game

NUM_BOARD_ROWS = 3
NUM_BOARD_COLS = 3
NUM_CONNECTS_TO_WIN = 3


def play_non_stop(game):
    while True:
        print("Starting a new game...")
        game.play()
        time.sleep(1)
        game.reset()


def main():
    print("Initializing game with players...")
    minimax_player = MinimaxPlayer("MiniMax Player", PlayerType.MaxPlayer, to_start=True)
    human_player = HumanPlayer("Human Player", PlayerType.MinPlayer)
    players = [minimax_player, human_player]
    g = Game(players, NUM_BOARD_ROWS, NUM_BOARD_COLS, NUM_CONNECTS_TO_WIN)
    for player in players:
        player.set_game(g.game_board)

    print("Starting to play tic-tac-toe")
    t = threading.Thread(target=play_non_stop, kwargs={'game': g})
    t.daemon = True
    t.start()

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(g)
    vis.run()


if __name__ == '__main__':
    main()
