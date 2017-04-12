#!/usr/bin/env python

import copy
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
        pass


class RandomPlayer(Player):
    def __init__(self, player_id, num_rows, num_cols):
        Player.__init__(self, player_id)
        self.num_rows = num_rows
        self.num_cols = num_cols

    def get_next_move(self, state):
        move = (random.randint(0, self.num_rows - 1),
                random.randint(0, self.num_cols - 1))
        return move


class HumanPlayer(Player):
    def __init__(self, player_id):
        Player.__init__(self, player_id)
        self.next_move = None

    def get_next_move(self, state):
        move = copy.deepcopy(self.next_move)
        self.next_move = None
        return move

    def handle_mouse_up_event(self, row_idx, col_idx):
        self.next_move = (row_idx, col_idx)
