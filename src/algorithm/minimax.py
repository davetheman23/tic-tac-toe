
from collections import deque
from sys import maxint


class MinimaxAlgorithm:
    def __init__(self, game):
        self.best_policy = {}
        self.game = game

    def get_best_policy(self, fresh=False):
        if not self.best_policy or fresh:
            self.best_policy = {}
            self._run_minimax()
        return self.best_policy

    def _initialize_best_value(self, player):
        if player.get_winning_reward() > self.game.get_draw_reward():
            return -maxint
        elif player.get_winning_reward() < self.game.get_draw_reward():
            return maxint
        else:
            raise RuntimeError("Cannot determine best initial value for player {}".format(str(player)))

    def _is_value_better(self, player, new_value, old_value):
        if player.get_winning_reward() > self.game.get_draw_reward():
            if new_value > old_value:
                return True
        elif player.get_winning_reward() < self.game.get_draw_reward():
            if new_value < old_value:
                return True
        else:
            raise RuntimeError("Cannot determine if value is improving for player {}".format(str(player)))
        return False

    def _run_minimax(self):
        if self.game.is_game_over():
            if self.game.get_winner() is None:
                return self.game.get_draw_reward()
            return self.game.get_winner().get_winning_reward()

        available_moves = self.game.get_available_moves()
        state = tuple(self.game.game_state)
        self.best_policy[state] = (self._initialize_best_value(self.game.current_player),
                                   next(iter(available_moves)))
        for move in available_moves:
            self.game.make_move(move)
            new_value = self._run_minimax()
            self.game.unmake_move(move)
            if self._is_value_better(self.game.current_player, new_value, self.best_policy[state][0]):
                self.best_policy[state] = (new_value, move)

        return self.best_policy[state][0]


class Game:
    NEUTRAL_MOVE_VALUE = 0

    def __init__(self, num_rows, num_cols, num_connects_to_win, players):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_connects_to_win = num_connects_to_win
        self.players = deque(players)
        self.current_player = self.players.popleft()

        self.game_state = [Game.NEUTRAL_MOVE_VALUE] * (self.num_rows * self.num_cols)
        self.played_moves = set()
        self.available_moves = set(range(self.num_rows * self.num_cols))
        self.winner = None

    def __str__(self):
        game_state_str = (('----' * self.num_cols + '\n').join(['|{:^3d}|' * self.num_cols + '\n'] * self.num_rows)
                          .format(*self.game_state))
        return "game state: \n{}\n".format(game_state_str)

    def is_connected(self, move_type, moves):
        for move in moves:
            if self.game_state[move] != move_type:
                return False
        return True

    def is_space_to_right(self, move):
        return move % self.num_cols + self.num_connects_to_win <= self.num_cols

    def is_space_down(self, move):
        return move + self.num_cols * (self.num_connects_to_win - 1) < self.num_rows * self.num_cols

    def is_space_to_left(self, move):
        return move % self.num_cols + 1 >= self.num_connects_to_win

    def is_game_over(self):
        if self.winner is not None:
            return True
        if not self.available_moves:
            return True

        for played_move in self.played_moves:
            move_type = self.game_state[played_move]
            if self.is_space_to_right(played_move):
                # if there is space to the right, need to evaluate right direction for connection
                right_connects = set(range(played_move, played_move + self.num_connects_to_win))
                if self.is_connected(move_type, right_connects):
                    self.winner = move_type
                    return True
                if self.is_space_down(played_move):
                    # if there is also space for down position, need to evaluate downright
                    down_right_connects = set(
                        (played_move + i * (self.num_cols + 1) for i in range(self.num_connects_to_win)))
                    if self.is_connected(move_type, down_right_connects):
                        self.winner = move_type
                        return True
            if self.is_space_down(played_move):
                # if there is space down, need to evaluate down direction for connection
                down_connects = set((played_move + i * self.num_cols for i in range(self.num_connects_to_win)))
                if self.is_connected(move_type, down_connects):
                    self.winner = move_type
                    return True
                if self.is_space_to_left(played_move):
                    # if there is also space to the left, need to evaluate down-left direction for connection
                    down_left_connects = set(
                        (played_move + i * (self.num_cols - 1) for i in range(self.num_connects_to_win)))
                    if self.is_connected(move_type, down_left_connects):
                        self.winner = move_type
                        return True
        return False

    def get_available_moves(self):
        return self.available_moves

    def get_winner(self):
        if self.winner is None:
            return None
        if self.current_player.get_winning_reward() == self.winner:
            return self.current_player
        for player in self.players:
            if player.get_winning_reward() == self.winner:
                return player
        return None

    def get_draw_reward(self):
        return Game.NEUTRAL_MOVE_VALUE

    def make_move(self, move):
        self.game_state[move] = self.current_player.get_winning_reward()
        self.played_moves.add(move)
        self.available_moves.remove(move)
        # change to next player's turn
        self.players.append(self.current_player)
        self.current_player = self.players.popleft()

    def unmake_move(self, move):
        self.game_state[move] = Game.NEUTRAL_MOVE_VALUE
        self.played_moves.remove(move)
        self.available_moves.add(move)
        # change to previous player's turn
        self.players.appendleft(self.current_player)
        self.current_player = self.players.pop()
        # when unmaking a move, it potentially reverted the winning state
        self.winner = None
