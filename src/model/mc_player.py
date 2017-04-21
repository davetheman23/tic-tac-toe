#!/usr/bin/env python

import player
import minimax_player
import random
import copy


class MCPlayer(player.Player):
    DEFAULT_EPSILON = 0.5
    GAMMA = 1.0

    def __init__(self, player_id):
        player.Player.__init__(self, player_id, player.PlayerType.MinPlayer)

        self.opponent = minimax_player.MinimaxPlayer("opponent")

        self.q_values = {}
        self.state_action_counts = {}

        self.learn_with_self_play(300)

    def get_next_move(self, state):
        action = self.get_epsilon_greedy_action(state, self.q_values, 0.0, True)

        i, j = action / 3, action % 3

        return i, j

    def learn(self, num_iterations):
        print("==================== Learning with Minimax Player ====================")
        for k in range(num_iterations):
            states, actions, rewards = self.run_episode()

            # Run the Monte Carlo update rules to get the new q-value function
            self.monte_carlo_update(states, actions, rewards, self.q_values, self.state_action_counts)
        print("====================     Done    ====================")

    @staticmethod
    def monte_carlo_update(states, actions, rewards, q_values, state_action_counts):
        # Update the state action counts (every-visit MC)
        for i in range(len(rewards)):
            state_action = (tuple(states[i]), actions[i])
            if state_action in state_action_counts:
                state_action_counts[state_action] += 1
            else:
                state_action_counts[state_action] = 1

        # Update the q-values for the states encountered in this episode
        for i in range(len(rewards)):
            state_action = (tuple(states[i]), actions[i])
            estimated_return = 0
            for j in range(i, len(rewards)):
                estimated_return += ((MCPlayer.GAMMA ** (j - i)) * rewards[j])

            if state_action in q_values:
                q_values[state_action] += ((1 / state_action_counts[state_action]) *
                                           (estimated_return - q_values[state_action]))
            else:
                q_values[state_action] = estimated_return

    def learn_with_self_play(self, num_iterations):
        print("==================== Learning with Self-Play ====================")
        first_player_q_values = {}
        first_player_state_action_counts = {}

        second_player_q_values = {}
        second_player_state_action_counts = {}

        for k in range(num_iterations):
            first_s, first_a, first_r, second_s, second_a, second_r = \
                self.run_episode_two_players(first_player_q_values,
                                             second_player_q_values)

            # Run the Monte Carlo update rule to get a new q-value function for the first player
            self.monte_carlo_update(first_s,
                                    first_a,
                                    first_r,
                                    first_player_q_values,
                                    first_player_state_action_counts)

            # Run the Monte Carlo update rule to get a new q-value function for the second player
            self.monte_carlo_update(second_s,
                                    second_a,
                                    second_r,
                                    second_player_q_values,
                                    second_player_state_action_counts)

        self.q_values = second_player_q_values
        print("====================     Done    ====================")

    def run_episode_two_players(self, first_player_q_values, second_player_q_values, epsilon=DEFAULT_EPSILON):
        s = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Store the first player's states, actions, and rewards
        first_s = []
        first_a = []
        first_r = []

        # Store the second player's states, actions, and rewards
        second_s = []
        second_a = []
        second_r = []

        i = 0
        while True:
            # Record the state for the first player
            first_s.append(copy.deepcopy(s))

            # First player takes an action
            first_player_action = self.get_epsilon_greedy_action(s, first_player_q_values, epsilon)
            first_a.append(first_player_action)
            s[first_player_action] = minimax_player.MinimaxPlayer.X

            # Check if we have reached a terminal state
            state = [[s[0], s[1], s[2]], [s[3], s[4], s[5]], [s[6], s[7], s[8]]]
            terminal, reward = minimax_player.MinimaxPlayer.is_terminal(state)
            if i > 0:
                # Record the second player's reward
                second_r.append(-reward)

            if terminal:
                # Record the first player's reward
                first_r.append(reward)

                break

            # Record the state for the second player
            second_s.append(copy.deepcopy(s))

            # Second player takes an action
            second_player_action = self.get_epsilon_greedy_action(s, second_player_q_values, epsilon)
            second_a.append(second_player_action)
            s[second_player_action] = minimax_player.MinimaxPlayer.O

            # Check if we have reached a terminal state
            state = [[s[0], s[1], s[2]], [s[3], s[4], s[5]], [s[6], s[7], s[8]]]
            terminal, reward = minimax_player.MinimaxPlayer.is_terminal(state)
            if i > 0:
                # Record the first player's reward
                first_r.append(reward)

            if terminal:
                # Record the first player's reward
                second_r.append(-reward)

                break

            i += 1

        print("Episode ended, first player's rewards: {}, second player's rewards: {}".format(first_r,
                                                                                              second_r))

        return first_s, first_a, first_r, second_s, second_a, second_r

    def play(self, num_iterations):
        print("==================== Playing against Minimax Player ====================")
        for k in range(num_iterations):
            states, actions, rewards = self.run_episode(0.0)

        print("====================     Done    ====================")

    def run_episode(self, epsilon=DEFAULT_EPSILON):
        """ Runs a single episode of tic-tac-toe and returns the trajectory of state, actions, and rewards """
        s = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        states = []
        actions = []
        rewards = []

        i = 0
        while True:
            # Opponent plays a move
            move_i, move_j = self.opponent.get_next_move(s)
            s[move_i * 3 + move_j] = minimax_player.MinimaxPlayer.X

            # TODO hacky
            ss = [[s[0], s[1], s[2]], [s[3], s[4], s[5]], [s[6], s[7], s[8]]]
            # print("Checking if {} is terminal...".format(ss))
            terminal, reward = minimax_player.MinimaxPlayer.is_terminal(ss)
            if i > 0:
                # Record the reward
                rewards.append(-reward)

            if terminal:
                print("Episode ended with reward {}".format(-reward))
                break

            # Record the current state
            states.append(copy.deepcopy(s))

            action = self.get_epsilon_greedy_action(s, self.q_values, epsilon)
            s[action] = minimax_player.MinimaxPlayer.O

            # Record the action taken
            actions.append(action)

            i += 1

        return states, actions, rewards

    @staticmethod
    def get_epsilon_greedy_action(state, q_values, epsilon=DEFAULT_EPSILON, verbose=False):
        """ Implements the epsilon-greedy policy """

        # Get the set of possible actions at this state
        actions = []
        for i in range(len(state)):
            if state[i] == 0:
                actions.append(i)

        if len(actions) == 0:
            print("No actions can be taken at state {}!".format(state))
            return None

        # Find the best action at this state according to the current q-values
        best_action_i = -1
        best_action_q = -1000000
        for i in range(len(actions)):
            state_action_q = 0
            state_action = (tuple(state), actions[i])
            if state_action in q_values:
                state_action_q = q_values[state_action]

            if state_action_q > best_action_q:
                best_action_q = state_action_q
                best_action_i = i

        action_probabilities = []
        for i in range(len(actions)):
            p = epsilon / len(actions)
            if i == best_action_i:
                p += (1 - epsilon)

            action_probabilities.append(p)

        if verbose:
            print("State is {}".format(state))
            for a, p in zip(actions, action_probabilities):
                sa = (tuple(state), a)
                q = 0.0 if sa not in q_values else q_values[sa]
                print("Action {} has q-value {} and prob {}".format(a, q, p))

        return MCPlayer.choose_with_probability(actions, action_probabilities)

    @staticmethod
    def choose_with_probability(choices, probabilities):
        r = random.random()
        i = 0
        while r >= 0 and i < len(probabilities):
            r -= probabilities[i]
            i += 1

        return choices[i - 1]

if __name__ == '__main__':
    p = MCPlayer("Monte Carlo Player")

    # p.learn(100)
    p.learn_with_self_play(200)
    p.play(50)

    # states, actions, rewards = p.run_episode()

    # for i in range(len(rewards)):
    #     print("s = {}, a = {}, r = {}".format(states[i], actions[i], rewards[i]))