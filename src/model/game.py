#!/usr/bin/env python

import time

from enum import Enum

from player import RandomPlayer

NUM_BOARD_ROWS = 4
NUM_BOARD_COLS = 4
NUM_WINNING_CONNECTS = 4

NO_SYMBOL = 0
X_SYMBOL = 1
O_SYMBOL = -1


class GameError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class BoardCell:
    class Direction(Enum):
        Right = (0, 1)
        DownRight = (1, 1)
        Down = (1, 0)
        DownLeft = (1, -1)

    def __init__(self, row_id, col_id, state=NO_SYMBOL):
        self.row_id = row_id
        self.col_id = col_id
        self.state = state
        self.downstream_neighbors = {
            BoardCell.Direction.Right: None,
            BoardCell.Direction.DownRight: None,
            BoardCell.Direction.Down: None,
            BoardCell.Direction.DownLeft: None
        }

    def __str__(self):
        return str("({}, {}): {}".format(self.row_id, self.col_id, self.state))

    def reset(self):
        self.__init__(self.row_id, self.col_id)

    def get_location(self):
        return self.row_id, self.col_id

    def add_downstream_neighbor(self, direction, cell=None):
        self.downstream_neighbors[direction] = cell

    def is_neighbor_matching(self, direction):
        neighbor = self.downstream_neighbors[direction]
        if neighbor is not None and neighbor.state == self.state:
            return True
        return False

    def get_all_matching_downstream_cells(self, direction):
        neighbor = self.downstream_neighbors[direction]
        if not self.is_neighbor_matching(direction):
            return []
        return [neighbor] + neighbor.get_all_matching_downstream_cells(direction)

    def get_max_of_downstream_neighbors(self):
        max_num_neighbors = 0
        for direction in BoardCell.Direction:
            neighbors = self.get_all_matching_downstream_cells(direction)
            if len(neighbors) > max_num_neighbors:
                max_num_neighbors = len(neighbors)
        return max_num_neighbors


class GameBoard:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cells = {(i, j): BoardCell(i, j) for i in range(num_rows) for j in range(num_cols)}
        # build the cell tree, just need to build it once, since all neighbors are stored by reference, changes in the
        # neighbor contents will be reflected when accessed
        for cell in self.cells.values():
            for direction in BoardCell.Direction:
                new_location = tuple(map(sum, zip(cell.get_location(), direction.value)))
                if new_location in self.cells:
                    cell.add_downstream_neighbor(direction, self.get_cell(*new_location))

    def get_cell(self, row_id, col_id):
        if (row_id, col_id) not in self.cells:
            raise ValueError("No cell at position ({}, {}) on the game board".format(row_id, col_id))
        return self.cells[(row_id, col_id)]

    def get_board_state(self):
        return [(location, cell.state) for location, cell in self.cells.iteritems()]

    def get_winning_state(self, num_win_connections=NUM_WINNING_CONNECTS):
        for cell in self.cells.values():
            if cell.state == NO_SYMBOL:
                continue
            if cell.get_max_of_downstream_neighbors() + 1 >= num_win_connections:
                return cell.state
        return NO_SYMBOL

    def are_moves_available(self):
        for cell in self.cells.values():
            if cell.state == NO_SYMBOL:
                return True
        return False

    def update_cell(self, row_id, col_id, state):
        self.get_cell(row_id, col_id).state = state

    def reset(self):
        for cell in self.cells:
            cell.reset()


class Game:
    MIN_NUM_PLAYERS = 2
    MAX_NUM_PLAYERS = 2

    def __init__(self, players):
        if len(players) < self.MIN_NUM_PLAYERS or len(players) > self.MAX_NUM_PLAYERS:
            raise GameError("Invalid number of players {}".format(str(len(players))))

        self.game_board = GameBoard(NUM_BOARD_ROWS, NUM_BOARD_COLS)
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
        return self.game_board.get_board_state()

    def get_next_player(self):
        """Returns the player whose turn is next"""
        if self.next_player_index < 0 or self.next_player_index >= len(self.players):
            raise GameError("Invalid next player index of {}".format(str(len(self.players))))

        return self.players[self.next_player_index]

    def is_terminated(self):
        """Returns true if the one of the players has won the model"""
        # Game is over if X or O wins
        winner = self.game_board.get_winning_state()
        if winner != NO_SYMBOL:
            if winner == X_SYMBOL:
                print("X wins!")
            else:
                print("O wins!")
            return True

        if self.game_board.are_moves_available():
            return False

        # No one is winning and the board is full (i.e. a draw)
        print("It's a draw!")
        return True

    def reset(self):
        """Resets the state of the model"""
        # Reset the next player count
        self.next_player_index = 0

        # Reset the model board
        self.game_board.reset()

    def make_move(self, player_index, location):
        """Makes a move for the specified player and location"""
        if player_index == 0:
            symbol = X_SYMBOL
        elif player_index == 1:
            symbol = O_SYMBOL
        else:
            raise GameError("Invalid player index of {}".format(str(player_index)))

        # Location must not already be occupied
        target_cell = self.game_board.get_cell(*location)
        if target_cell.state != NO_SYMBOL:
            raise GameError("Board location of ({}, {}) is already occupied!".format(*location))

        target_cell.state = symbol
        self.next_player_index = (self.next_player_index + 1) % len(self.players)

    def print_game_board(self):
        print("=========" * NUM_BOARD_COLS)
        print(('--------' * NUM_BOARD_COLS + '\n').join(['|{:^6s}|' * NUM_BOARD_COLS + '\n'] * NUM_BOARD_ROWS)
              .format(*[str(self.game_board.get_cell(i, j).state)
                        for i in range(NUM_BOARD_ROWS)
                        for j in range(NUM_BOARD_COLS)]))
        print("=========" * NUM_BOARD_COLS)


if __name__ == '__main__':
    s = Game([RandomPlayer(0, NUM_BOARD_ROWS, NUM_BOARD_COLS), RandomPlayer(1, NUM_BOARD_ROWS, NUM_BOARD_COLS)])
    s.play()
