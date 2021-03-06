#!/usr/bin/env python

import copy
import random

from abc import ABCMeta, abstractmethod
from enum import Enum
from sys import maxint

import src.algorithm.minimax as minimax_lib
import src.algorithm.learning_agents as rl_lib


class PlayerType(Enum):
    MaxPlayer = 1
    MinPlayer = -1


class Player:
    __metaclass__ = ABCMeta

    def __init__(self, player_id, player_type):
        self.player_id = player_id
        self.type = player_type
        self.game = None

    def __str__(self):
        return "'{}'".format(self.player_id)

    def get_id(self):
        return self.player_id

    def get_winning_reward(self):
        # for now, simply use the enum value as the winning reward, which can actually be a function of the player type
        return self.type.value

    @abstractmethod
    def get_next_move(self, state):
        pass

    def set_game(self, game):
        """Tell the player what game we are playing"""
        self.game = game


class RandomPlayer(Player):
    def __init__(self, player_id, player_type):
        Player.__init__(self, player_id, player_type)

    def get_next_move(self, state):
        moves = random.sample(self.game.game_board.get_available_game_positions(), 1)
        if len(moves) == 0:
            raise RuntimeError("No moves available")
        return self.game.game_board.convert_position_to_cell_location(moves[0])


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
    def __init__(self, player_id, player_type, to_start):
        if player_type != PlayerType.MaxPlayer and player_type != PlayerType.MinPlayer:
            raise RuntimeError("Player type '{}' not supported, only allow min or max player type for minmax player."
                               .format(player_type))

        Player.__init__(self, player_id, player_type)
        # should be an instance of GameBoard
        self.to_start = to_start
        self.policy = {}
        if self.game is not None:
            self._build_minimax_action_policy()

    def set_game(self, game_board):
        super(MinimaxPlayer, self).set_game(game_board)
        self._build_minimax_action_policy()

    def get_next_move(self, state):
        if not self.policy:
            self._build_minimax_action_policy()
        if state not in self.policy:
            raise RuntimeError("No action policy for current game state.")
        return self.game.game_board.convert_position_to_cell_location(self.policy[state])

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

        g = minimax_lib.Game(self.game.game_board.num_rows, self.game.game_board.num_cols,
                             self.game.game_board.num_connects_to_win, players)
        minimax = minimax_lib.MinimaxAlgorithm(g)
        print("building best action policies according to minimax algorithm")
        best_policy = minimax.get_best_policy()
        for state, policy in best_policy.iteritems():
            _, move = policy
            self.policy[state] = move
        print("Finished building best action policies according to minimax algorithm")


class MCPlayer(Player, rl_lib.MonteCarloAgent):

    def __init__(self, player_id, player_type):
        Player.__init__(self, player_id, player_type)
        rl_lib.MonteCarloAgent.__init__(self)

    def get_next_move(self, state):
        if self.game is None:
            raise RuntimeError("No game is set to the player. The player needs to have a reference to the game.")

        best_move = self.get_estimated_best_move(state, self.game.game_board.get_available_game_positions())
        state_action_pair = (state, best_move)
        self.trajectory.append(state_action_pair)
        if state_action_pair not in self.visitation_counts:
            self.visitation_counts[state_action_pair] = 0
        self.visitation_counts[state_action_pair] += 1

        return self.game.game_board.convert_position_to_cell_location(best_move)
