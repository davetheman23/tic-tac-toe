import logging
import random

from abc import ABCMeta, abstractmethod
from enum import Enum
from sys import maxint


class Mode(Enum):
    Learn = 1
    Play = 2
    Adaptive = 3

logger = logging.getLogger(file.__name__)


class Agent:
    __metaclass__ = ABCMeta

    def __init__(self):
        # experience is what the agent has seen so far, it is a dictionary of (state, action) to reward
        self.experiences = {}
        self.mode = Mode.Adaptive

    def set_mode(self, mode):
        self.mode = mode

    @abstractmethod
    def evaluate_game_state(self, state):
        """define how the game should be evaluated, such as what rewards we are getting, used to build up experience"""
        pass

    @abstractmethod
    def get_estimated_best_move(self, state, available_positions):
        """defines the policy of this agent, as to what it thinks as the best move given a state"""
        pass


class MonteCarloAgent(Agent):
    LOSE_REWARD = -10
    INDETERMINITE_REWARD = 0
    DRAW_REWARD = 2
    WIN_REWARD = 10

    GAMMA = 1

    def __init__(self):
        super(MonteCarloAgent, self).__init__()

        self.trajectory = []
        self.trajectory_rewards = []
        self.visitation_counts = {}

        self.games_played = 0
        self.verbose = False

    def set_mode(self, mode):
        self.mode = mode
        self.verbose = self.mode == Mode.Play

    def evaluate_game_state(self, game):
        winner = game.get_winner()
        if winner is None:
            if len(game.game_board.get_available_game_positions()) == 0:
                # then it is a draw
                reward = MonteCarloAgent.DRAW_REWARD
            else:
                # the game hasn't ended after this position
                reward = MonteCarloAgent.INDETERMINITE_REWARD
        elif winner == self:
            # it is a win
            reward = MonteCarloAgent.WIN_REWARD
        else:
            # if the other player wins after this player made the last move
            reward = MonteCarloAgent.LOSE_REWARD
        self.trajectory_rewards.append(reward)

    def evaluate_game_board_final_state(self, game):
        self.games_played += 1
        # evaluate game board's state at the end of the
        self.evaluate_game_state(game)
        for i, state_action_pair in enumerate(self.trajectory):
            estimated_return = 0
            for j in range(i, len(self.trajectory_rewards)):
                estimated_return += TDPlayer.GAMMA ** (j - i) * self.trajectory_rewards[j]
            if state_action_pair not in self.experiences:
                self.experiences[state_action_pair] = 0.0
            self.experiences[state_action_pair] += 1.0 / self.visitation_counts[state_action_pair] * \
                (estimated_return - self.experiences[state_action_pair])

        self.trajectory = []
        self.trajectory_rewards = []

    def get_estimated_best_move(self, state, available_positions):
        best_value = -maxint
        best_position = None
        not_visited_positions = []
        if self.verbose:
            print("Current state is : {}".format(state))
        for available_position in available_positions:
            if (state, available_position) in self.experiences:
                if self.experiences[(state, available_position)] > best_value:
                    best_value = self.experiences[(state, available_position)]
                    best_position = available_position
            else:
                not_visited_positions.append(available_position)
            if self.verbose:
                if (state, available_position) not in self.visitation_counts:
                    q_val = -maxint
                    num_visits = 0
                else:
                    q_val = self.experiences[(state, available_position)]
                    num_visits = self.visitation_counts[(state, available_position)]
                print("Action {}: q-value {} (visited {} times)".format(available_position, q_val, num_visits))
        if best_position is not None:
            if self.verbose:
                print("Best action is {}".format(best_position))
            if self.mode == Mode.Learn and random.randint(0, 10) <= 2:
                return best_position
            if self.mode == Mode.Play:
                if best_value < MonteCarloAgent.DRAW_REWARD and len(not_visited_positions) > 0:
                    if self.verbose:
                        print("best position resulting in non-winning result, resetting the available actions "
                              "to non-visited positions {}".format(not_visited_positions))
                    available_positions = not_visited_positions
                else:
                    return best_position

        positions = random.sample(available_positions, 1)
        if self.verbose:
            print("Choosing a random action {}".format(positions[0]))
        return positions[0]


class TDPlayer(Agent):
    LOSE_REWARD = -10
    INDETERMINITE_REWARD = 0
    DRAW_REWARD = 2
    WIN_REWARD = 10

    ALPHA = 0.1
    GAMMA = 0.6

    def __init__(self):
        super(TDPlayer, self).__init__()

        self.last_state = None
        self.last_move = None

    def evaluate_game_state(self, game):
        pass
        # evaluate the current game state, and reward the player for its last action accordingly
        # winning_state = self.game_board.get_winning_state()
        # if winning_state == self.type.value:
        #     # it is a win
        #     reward = TDPlayer.WIN_REWARD
        # elif winning_state == 0:
        #     if len(self.game_board.get_available_game_positions()) == 0:
        #         # then it is a draw
        #         reward = TDPlayer.DRAW_REWARD
        #     else:
        #         # the game hasn't ended after this position
        #         reward = TDPlayer.INDETERMINITE_REWARD
        # else:
        #     # if the other player wins after this player made the last move
        #     reward = TDPlayer.LOSE_REWARD
        #
        # # use the reward to define the value function of the current game state
        # current_game_state = self.game_board.encode_cell_state(self.game_board.get_board_state())
        # self.experiences[current_game_state] = reward
        #
        # # use the reward we have determined to update the action value from my previous state
        # state_action_pair = (self.last_state, self.last_move)
        # if state_action_pair not in self.experiences:
        #     self.experiences[state_action_pair] = self.INDETERMINITE_REWARD
        # self.experiences[state_action_pair] += TDPlayer.ALPHA * \
        #     (reward + TDPlayer.GAMMA * self.experiences[current_game_state] - self.experiences[state_action_pair])

    def get_estimated_best_move(self, state, available_positions):
        pass
        # available_positions = self.game_board.get_available_game_positions()
        # negative_positions = set()
        # best_value = -maxint
        # best_position = None
        # for available_position in available_positions:
        #     if (state, available_position) in self.experiences:
        #         if self.experiences[(state, available_position)] > best_value:
        #             best_value = self.experiences[(state, available_position)]
        #             best_position = available_position
        #         if self.experiences[(state, available_position)] < 0:
        #             negative_positions.add(available_position)
        # if best_position is not None:
        #     if best_value >= TDPlayer.WIN_REWARD:
        #         # it is good enough, in all the available states, we will just play it
        #         return best_position
        #
        # print("None of the moves seems to yield a winning state, so just choose any non-negative positions to play")
        # non_negative_positions = available_positions.difference(negative_positions)
        # if len(non_negative_positions) > 0:
        #     available_positions = non_negative_positions
        #
        # positions = random.sample(available_positions, 1)
        # return positions[0]
