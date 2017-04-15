
from collections import deque
from sys import maxint
from enum import Enum
#from model.player import PlayerType


class PlayerType(Enum):
    MinPlayer = -1
    MaxPlayer = 1


def evaluate(game):
    if game.get_winner() == PlayerType.MaxPlayer.value:
        return 1
    elif game.get_winner() == PlayerType.MinPlayer.value:
        return -1
    return 0


def initialize_best_value(player_type):
    if player_type == PlayerType.MaxPlayer:
        return -maxint
    elif player_type == PlayerType.MinPlayer:
        return maxint
    else:
        raise RuntimeError("player type {} not recognized".format(player_type))


def is_value_better(player_type, new_value, old_value):
    if player_type == PlayerType.MaxPlayer:
        if new_value > old_value:
            return True
    elif player_type == PlayerType.MinPlayer:
        if new_value < old_value:
            return True
    else:
        raise RuntimeError("player type {} not recognized".format(player_type))
    return False

best_policy = {}


def minimax(game):
    if not isinstance(game, Game):
        raise ValueError("Game should be of type '{}'".format(type(Game)))
    if game.is_game_over():
        return evaluate(game)
    available_moves = game.get_available_moves()
    state = tuple(game.game_state)
    best_policy[state] = (initialize_best_value(game.current_player.type), next(iter(available_moves)))
    for move in available_moves:
        game.make_move(move)
        new_value = minimax(game)
        game.unmake_move(move)
        if is_value_better(game.current_player.type, new_value, best_policy[state][0]):
            best_policy[state] = (new_value, move)

    return best_policy[state][0]


class Game:
    NEUTRAL_MOVE_TYPE = 0

    def __init__(self, num_rows, num_cols, num_connects_to_win, players):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_connects_to_win = num_connects_to_win
        self.players = deque(players)
        self.current_player = self.players.popleft()

        self.game_state = [Game.NEUTRAL_MOVE_TYPE] * (self.num_rows * self.num_cols)
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
                        [played_move + i * (self.num_cols + 1) for i in range(self.num_connects_to_win)])
                    if self.is_connected(move_type, down_right_connects):
                        self.winner = move_type
                        return True
            if self.is_space_down(played_move):
                # if there is space down, need to evaluate down direction for connection
                down_connects = set([played_move + i * self.num_cols for i in range(self.num_connects_to_win)])
                if self.is_connected(move_type, down_connects):
                    self.winner = move_type
                    return True
                if self.is_space_to_left(played_move):
                    # if there is also space to the left, need to evaluate down-left direction for connection
                    down_left_connects = set(
                        [played_move + i * (self.num_cols - 1) for i in range(self.num_connects_to_win)])
                    if self.is_connected(move_type, down_left_connects):
                        self.winner = move_type
                        return True
        return False

    def get_available_moves(self):
        return self.available_moves

    def get_winner(self):
        return self.winner

    def make_move(self, move):
        self.game_state[move] = self.current_player.type.value
        self.played_moves.add(move)
        self.available_moves.remove(move)
        # change to next player's turn
        self.players.append(self.current_player)
        self.current_player = self.players.popleft()


    def unmake_move(self, move):
        self.game_state[move] = Game.NEUTRAL_MOVE_TYPE
        self.played_moves.remove(move)
        self.available_moves.add(move)
        # change to previous player's turn
        self.players.appendleft(self.current_player)
        self.current_player = self.players.pop()
        # when unmaking a move, it potentially reverted the winning state
        self.winner = None


class Player:
    def __init__(self, player_type):
        self.type = player_type

import random
import time

NUM_COLS = 4
NUM_ROWS = 4
NUM_CONNECTS_TO_WIN = 3

if __name__ == '__main__':
    for NUM_ROWS in range(3, 6):
        for NUM_COLS in range(3, 6):
            NUM_CONNECTS_TO_WIN = max(min(NUM_ROWS, NUM_COLS) - 1, 3)
            g = Game(NUM_ROWS, NUM_COLS, NUM_CONNECTS_TO_WIN, [Player(PlayerType.MaxPlayer), Player(PlayerType.MinPlayer)])
            print("building best policies according to minimax algorithm")
            start = time.clock()
            minimax_val = minimax(g)
            end = time.clock()
            print("Total time to build minimax best policy is: {} seconds".format(str(end - start)))

            with open("game_results_{}_{}.txt".format(NUM_ROWS, NUM_COLS), "w") as f:
                print("Running games of size {} x {} ...".format(NUM_ROWS, NUM_COLS))
                f.write("Total time to build minimax best policy is: {} seconds".format(str(end - start)))
                for game_idx in range(10):
                    print("Running game {}".format(game_idx))
                    f.write("\n#########################################\n")
                    f.write("Start playing game {}\n".format(game_idx))
                    g = Game(NUM_ROWS, NUM_COLS, NUM_CONNECTS_TO_WIN, [Player(PlayerType.MaxPlayer), Player(PlayerType.MinPlayer)])
                    # set a random start location
                    g.make_move(random.randint(0, NUM_ROWS * NUM_COLS - 1))
                    f.write(str(g) + "\n")
                    f.write("============\n")
                    while not g.is_game_over():
                        time.sleep(0.1)
                        minimax_move = best_policy[tuple(g.game_state)][1]
                        g.make_move(minimax_move)
                        f.write(str(g) + "\n")
                        f.write("============\n")
                    winner = g.get_winner()
                    if winner == 0:
                        f.write("its a draw\n")
                        print("its a draw")
                    else:
                        f.write("the winner is {}\n".format(winner))
                        print("the winner is {}".format(winner))


