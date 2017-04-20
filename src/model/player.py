#!/usr/bin/env python

import copy
import random

from abc import ABCMeta, abstractmethod
from enum import Enum
from sys import maxint

import src.algorithm.minimax as minimax_lib


class PlayerType(Enum):
    MaxPlayer = 1
    MinPlayer = -1


class Player:
    __metaclass__ = ABCMeta

    def __init__(self, player_id, player_type):
        self.player_id = player_id
        self.type = player_type
        self.game_board = None

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

    def set_game(self, game_board):
        """Tell the player what game we are playing"""
        self.game_board = game_board


class RandomPlayer(Player):
    def __init__(self, player_id, player_type):
        Player.__init__(self, player_id, player_type)

    def get_next_move(self, state):
        moves = random.sample(self.game_board.get_available_game_positions(), 1)
        if len(moves) == 0:
            raise RuntimeError("No moves available")
        return self.game_board.convert_position_to_cell_location(moves[0])


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
        if self.game_board is not None:
            self._build_minimax_action_policy()

    def set_game(self, game_board):
        super(MinimaxPlayer, self).set_game(game_board)
        self._build_minimax_action_policy()

    def get_next_move(self, state):
        if not self.policy:
            self._build_minimax_action_policy()
        if state not in self.policy:
            raise RuntimeError("No action policy for current game state.")
        return self.game_board.convert_position_to_cell_location(self.policy[state])

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

        g = minimax_lib.Game(self.game_board.num_rows, self.game_board.num_cols,
                             self.game_board.num_connects_to_win, players)
        minimax = minimax_lib.MinimaxAlgorithm(g)
        print("building best action policies according to minimax algorithm")
        best_policy = minimax.get_best_policy()
        for state, policy in best_policy.iteritems():
            _, move = policy
            self.policy[state] = move
        print("Finished building best action policies according to minimax algorithm")


class TDPlayer(Player):
    LOSE_REWARD = -10
    INDETERMINITE_REWARD = 0
    DRAW_REWARD = 2
    WIN_REWARD = 10

    ALPHA = 0.1
    GAMMA = 0.6

    class Mode(Enum):
        Learn = "Learn"
        Play = "Play"

    def __init__(self, player_id, player_type):
        Player.__init__(self, player_id, player_type)
        # experience is what the agent has seen so far, it is a dictionary of (state, action) to reward
        self.experiences = {}
        self.mode = TDPlayer.Mode.Learn
        self.last_state = None
        self.last_move = None

    def set_mode(self, mode):
        self.mode = mode

    def get_next_move(self, state):
        if self.game_board is None:
            raise RuntimeError("No game is set to the player. The player needs to have a reference to the game.")

        if self.mode == TDPlayer.Mode.Play:
            self.last_state = state
            best_move = self.get_estimated_best_move(state)
            self.last_move = best_move
        elif self.mode == TDPlayer.Mode.Learn:
            self.last_state = state
            # when we are learning, just play random moves
            moves = random.sample(self.game_board.get_available_game_positions(), 1)
            self.last_move = moves[0]
        return self.game_board.convert_position_to_cell_location(self.last_move)

    def evaluate_game_board(self):
        # evaluate the current game state, and reward the player for its last action accordingly
        winning_state = self.game_board.get_winning_state()
        if winning_state == self.type.value:
            # it is a win
            reward = TDPlayer.WIN_REWARD
        elif winning_state == 0:
            if len(self.game_board.get_available_game_positions()) == 0:
                # then it is a draw
                reward = TDPlayer.DRAW_REWARD
            else:
                # the game hasn't ended after this position
                reward = TDPlayer.INDETERMINITE_REWARD
        else:
            # if the other player wins after this player made the last move
            reward = TDPlayer.LOSE_REWARD

        # use the reward to define the value function of the current game state
        current_game_state = self.game_board.encode_cell_state(self.game_board.get_board_state())
        self.experiences[current_game_state] = reward

        # use the reward we have determined to update the action value from my previous state
        state_action_pair = (self.last_state, self.last_move)
        if state_action_pair not in self.experiences:
            self.experiences[state_action_pair] = self.INDETERMINITE_REWARD
        self.experiences[state_action_pair] += TDPlayer.ALPHA * \
            (reward + TDPlayer.GAMMA * self.experiences[current_game_state] - self.experiences[state_action_pair])

    def get_estimated_best_move(self, state):
        available_positions = self.game_board.get_available_game_positions()
        negative_positions = set()
        best_value = -maxint
        best_position = None
        for available_position in available_positions:
            if (state, available_position) in self.experiences:
                if self.experiences[(state, available_position)] > best_value:
                    best_value = self.experiences[(state, available_position)]
                    best_position = available_position
                if self.experiences[(state, available_position)] < 0:
                    negative_positions.add(available_position)
        if best_position is not None:
            if best_value >= TDPlayer.WIN_REWARD:
                # it is good enough, in all the available states, we will just play it
                return best_position

        print("None of the moves seems to yield a winning state, so just choose any non-negative positions to play")
        non_negative_positions = available_positions.difference(negative_positions)
        if len(non_negative_positions) > 0:
            available_positions = non_negative_positions

        positions = random.sample(available_positions, 1)
        return positions[0]
