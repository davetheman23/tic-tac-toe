#!/usr/bin/env python

import copy
import random

from abc import ABCMeta, abstractmethod
from enum import Enum

import src.algorithm.minimax as minimax_lib


class PlayerType(Enum):
    MaxPlayer = 1
    MinPlayer = -1


class Player:
    __metaclass__ = ABCMeta

    def __init__(self, player_id, player_type):
        self.player_id = player_id
        self.type = player_type

        # for now, simply use the enum value as the winning reward, which can actually be a function of the player type
        self.winning_reward = player_type.value

    def __str__(self):
        return "'{}'".format(self.player_id)

    def get_id(self):
        return self.player_id

    def get_winning_reward(self):
        return self.winning_reward

    @abstractmethod
    def get_next_move(self, state):
        pass


class RandomPlayer(Player):
    def __init__(self, player_id, player_type, num_rows, num_cols):
        Player.__init__(self, player_id, player_type)
        self.num_rows = num_rows
        self.num_cols = num_cols

    def get_next_move(self, state):
        move = (random.randint(0, self.num_rows - 1),
                random.randint(0, self.num_cols - 1))
        return move


class HumanPlayer(Player):
    def __init__(self, player_id, player_type):
        Player.__init__(self, player_id, player_type)
        self.next_move = None

    def get_next_move(self, state):
        move = copy.deepcopy(self.next_move)
        self.next_move = None
        return move

    def handle_mouse_up_event(self, row_idx, col_idx):
        self.next_move = (row_idx, col_idx)


class MinimaxPlayer(Player):
    def __init__(self, player_id, player_type, num_rows, num_cols, num_connects_to_win, to_start):
        if player_type != PlayerType.MaxPlayer and player_type != PlayerType.MinPlayer:
            raise RuntimeError("Player type '{}' not supported, only allow min or max player type for minmax player."
                               .format(player_type))

        Player.__init__(self, player_id, player_type)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_connects_to_win = num_connects_to_win
        self.to_start = to_start
        self.moves = {}

    def get_next_move(self, state):
        """
        Get the next move to play by the player

        :param state: a list of (location, cell state), where location is just (row_id, col_id).  
        :return: a tuple of (row_id, col_id)
        """
        encoded_state = self._encoding(state)
        if not self.moves:
            self._build_minimax_action_policy()
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

    def _build_minimax_action_policy(self):
        clone_player = copy.deepcopy(self)
        if self.type == PlayerType.MinPlayer:
            clone_player.type = PlayerType.MaxPlayer
        elif self.type == PlayerType.MaxPlayer:
            clone_player.type = PlayerType.MinPlayer

        if self.to_start:
            players = [self, clone_player]
        else:
            players = [clone_player, self]

        g = minimax_lib.Game(self.num_rows, self.num_cols, self.num_connects_to_win, players)
        minimax = minimax_lib.MinimaxAlgorithm(g)
        print("building best action policies according to minimax algorithm")
        self.moves = minimax.get_best_policy()
        print("Finished building best action policies according to minimax algorithm")
