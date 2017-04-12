#!/usr/bin/env python

import threading

from view.visualizer import Visualizer
from model.player import RandomPlayer, HumanPlayer
from model.game import Game


def main():
    s = Game([RandomPlayer(0), HumanPlayer(1)])

    print("Starting to play tic-tac-toe")
    t = threading.Thread(target=s.play)
    t.daemon = True
    t.start()

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(s)
    vis.run()


if __name__ == '__main__':
    main()
