#!/usr/bin/env python

import time

from player import RandomPlayer

NUM_BOARD_ROWS = 3
NUM_BOARD_COLS = 3

NO_SYMBOL = 0
X_SYMBOL = 1
O_SYMBOL = -1


class GameError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Game:
    MIN_NUM_PLAYERS = 2
    MAX_NUM_PLAYERS = 2

    def __init__(self, players):
        if len(players) < self.MIN_NUM_PLAYERS or len(players) > self.MAX_NUM_PLAYERS:
            raise GameError("Invalid number of players {}".format(str(len(players))))

        self.game_board_state = [[NO_SYMBOL for i in range(NUM_BOARD_ROWS)] for j in range(NUM_BOARD_COLS)]
        self.next_player_index = 0
        self.players = players

    def play(self):
        """The main play loop of the model"""
        while not self.is_terminated():
            try:
                next_player = self.get_next_player()
                move = next_player.get_next_move(self.get_game_board_state())
                if move is None:
                    # if no move available just skip
                    time.sleep(0.1)
                    continue
                self.make_move(self.next_player_index, move)
                self.print_game_board()
                time.sleep(1)
            except GameError as e:
                print(e.msg)

    def get_game_board_state(self):
        return self.game_board_state

    def get_next_player(self):
        """Returns the player whose turn is next"""
        if self.next_player_index < 0 or self.next_player_index >= len(self.players):
            raise GameError("Invalid next player index of {}".format(str(len(self.players))))

        return self.players[self.next_player_index]

    def is_terminated(self):
        """Returns true if the one of the players has won the model"""
        # Game is over if X or O wins
        winner = self.get_winner()
        if winner != NO_SYMBOL:
            if winner == X_SYMBOL:
                print("X wins!")
            else:
                print("O wins!")

            return True

        # Game is over if the board is full (i.e. a draw)
        for i in range(3):
            for j in range(3):
                if self.game_board_state[i][j] == NO_SYMBOL:
                    return False

        print("It's a draw!")
        return True

    def get_winner(self):
        """Returns X_SYMBOL if the X player has won, O_SYMBOL if the O player has won, and NO_SYMBOL otherwise"""
        # Compute the row, column, and diagonal sums
        row_sums = map(sum, self.game_board_state)
        col_sums = map(sum, [list(column) for column in zip(*self.game_board_state)])
        left_diag_sum = 0
        right_diag_sum = 0

        for i in range(3):
            left_diag_sum += self.game_board_state[i][i]
            right_diag_sum += self.game_board_state[i][2 - i]

        # Check if a player has won on the diagonal
        if left_diag_sum == 3 * X_SYMBOL or right_diag_sum == 3 * X_SYMBOL:
            return X_SYMBOL
        elif left_diag_sum == 3 * O_SYMBOL or left_diag_sum == 3 * O_SYMBOL:
            return O_SYMBOL

        # The row/column sums indicate if a player has won along a row or column
        for s in (row_sums + col_sums):
            if s == 3 * X_SYMBOL:
                return X_SYMBOL
            elif s == 3 * O_SYMBOL:
                return O_SYMBOL

        # Otherwise, there is no winner yet or it is a draw
        return NO_SYMBOL

    def reset(self):
        """Resets the state of the model"""
        # Reset the next player count
        self.next_player_index = 0

        # Reset the model board
        for i in range(3):
            for j in range(3):
                self.game_board_state[i][j] = NO_SYMBOL

    def make_move(self, player_index, location):
        """Makes a move for the specified player and location"""
        if player_index == 0:
            symbol = X_SYMBOL
        elif player_index == 1:
            symbol = O_SYMBOL
        else:
            raise GameError("Invalid player index of {}".format(str(player_index)))

        i = location[0]
        j = location[1]

        # Location must not already be occupied
        if self.game_board_state[i][j] != NO_SYMBOL:
            raise GameError("Board location of ({cell_i}, {cell_j}) is already occupied!".format(cell_i=str(i),
                                                                                                 cell_j=str(j)))

        self.game_board_state[i][j] = symbol
        self.next_player_index = (self.next_player_index + 1) % len(self.players)

    def print_game_board(self):
        # flattened = [x for row in self.game_board_state for x in row]
        print("{}|{}|{}\n------\n{}|{}|{}\n------\n{}|{}|{}\n".format(self.game_board_state[0][0],
                                                                      self.game_board_state[0][1],
                                                                      self.game_board_state[0][2],
                                                                      self.game_board_state[1][0],
                                                                      self.game_board_state[1][1],
                                                                      self.game_board_state[1][2],
                                                                      self.game_board_state[2][0],
                                                                      self.game_board_state[2][1],
                                                                      self.game_board_state[2][2]))

if __name__ == '__main__':
    s = Game([RandomPlayer(0), RandomPlayer(1)])
    s.play()
