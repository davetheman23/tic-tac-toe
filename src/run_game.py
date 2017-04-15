#!/usr/bin/env python

import threading

from view.visualizer import Visualizer
from model.player import RandomPlayer, HumanPlayer, MinimaxPlayer, PlayerType
from model.game import Game

NUM_BOARD_ROWS = 3
NUM_BOARD_COLS = 3
NUM_CONNECTS_TO_WIN = 3


def main():
    # random_player = RandomPlayer("Random Player", PlayerType.MaxPlayer, NUM_BOARD_ROWS, NUM_BOARD_COLS)
    human_player = HumanPlayer("Human Player", PlayerType.MinPlayer)
    minimax_player = MinimaxPlayer("MiniMax Player", PlayerType.MaxPlayer,
                                   NUM_BOARD_ROWS, NUM_BOARD_COLS, NUM_CONNECTS_TO_WIN, False)

    players = [human_player, minimax_player]
    s = Game(players, NUM_BOARD_ROWS, NUM_BOARD_COLS, NUM_CONNECTS_TO_WIN)

    print("Starting to play tic-tac-toe")
    t = threading.Thread(target=s.play)
    t.daemon = True
    t.start()

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(s)
    vis.run()


if __name__ == '__main__':
    main()
