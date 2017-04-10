#!/usr/bin/env python

import threading

from view.visualizer import Visualizer
from simulator.player import RandomPlayer, HumanPlayer
from simulator.simulator import Simulator


def main():
    #s = Simulator([RandomPlayer(0), HumanPlayer(1)])
    s = Simulator([RandomPlayer(0), RandomPlayer(0)])

    print("Setting up visualization daemon thread ...")
    vis = Visualizer(s)
    t = threading.Thread(target=vis.run)
    t.daemon = True
    t.start()

    print("Starting to play tic-tac-toe")
    s.play()


if __name__ == '__main__':
    main()
