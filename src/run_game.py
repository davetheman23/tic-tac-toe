#!/usr/bin/env python

import threading

from view.visualizer import Visualizer
from simulator.player import RandomPlayer, HumanPlayer
from simulator.simulator import Simulator


def main():
    s = Simulator([RandomPlayer(0), HumanPlayer(1)])

    print("Starting to play tic-tac-toe")
    t = threading.Thread(target=s.play)
    t.daemon = True
    t.start()

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(s)
    vis.run()


if __name__ == '__main__':
    main()
