#!/usr/bin/env python

import copy
import random

from abc import ABCMeta, abstractmethod

#from model.game import NO_SYMBOL, X_SYMBOL, O_SYMBOL


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


class MinimaxPlayer(Player):
    def __init__(self, player_id, player_type, num_rows, num_cols):
        Player.__init__(self, player_id)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.moves = {}
        self.build_minimax_action_policy()

    def get_next_move(self, state):
        """
        Get the next move to play by the player

        :param state: a list of (location, cell state), where location is just (row_id, col_id).  
        :return: a tuple of (row_id, col_id)
        """
        encoded_state = self._encoding(state)
        if not self.moves:
            self.build_minimax_action_policy(encoded_state)
        if encoded_state not in self.moves:
            raise RuntimeError("No action policy for current game state.")
        return self.moves[encoded_state]

    def _encoding(self, state):
        """
        Encode the game state into an internal representation understood by the player
        
        :param state: a list of (location, cell state), where location is just (row_id, col_id).  
        :return: an internal representation of the game state, which is a tuple of all cell state sequenced by joining
                  each row together
        """
        encoded_state = [0] * (self.num_rows * self.num_cols)
        for cell_location, cell_state in state:
            row_idx, col_idx = cell_location
            position = row_idx * self.num_cols + col_idx
            encoded_state[position] = cell_state
        return tuple(encoded_state)

    def build_minimax_action_policy(self, encoded_state):
        pass
