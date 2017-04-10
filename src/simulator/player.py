#!/usr/bin/env python

import random

from abc import ABCMeta, abstractmethod


class Player:
    __metaclass__ = ABCMeta

    def __init__(self, player_id):
        self.player_id = player_id

    def get_id(self):
        return self.player_id

    @abstractmethod
    def get_next_move(self, state):
        return None


class RandomPlayer(Player):
    def __init__(self, player_id):
        Player.__init__(self, player_id)

    def get_next_move(self, state):
        move = (random.randint(0, 2),
                random.randint(0, 2))
        return move


class HumanPlayer(Player):
    def __init__(self, player_id):
        Player.__init__(self, player_id)
        self.waiting = False

    def get_next_move(self):
        self.waiting = True
        pass

    def handle_mouse_up_event(self):
        pass
