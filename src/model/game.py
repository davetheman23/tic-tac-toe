#!/usr/bin/env python

import copy
import time

from enum import Enum

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
        self.state = NO_SYMBOL

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
    def __init__(self, num_rows, num_cols, num_connects_to_win):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_connects_to_win = num_connects_to_win
        self.available_positions = set()
        self.cells = {(i, j): BoardCell(i, j) for i in range(num_rows) for j in range(num_cols)}
        # build the cell tree, just need to build it once, since all neighbors are stored by reference, changes in the
        # neighbor contents will be reflected when accessed
        for location, cell in self.cells.iteritems():
            self.available_positions.add(self.convert_cell_location_to_position(location))
            for direction in BoardCell.Direction:
                new_location = tuple(map(sum, zip(cell.get_location(), direction.value)))
                if new_location in self.cells:
                    cell.add_downstream_neighbor(direction, self.get_cell(new_location))
        self.positions = set(self.cells.keys())

    def get_cell(self, location):
        if location not in self.cells:
            raise ValueError("No cell at position ({}, {}) on the game board".format(*location))
        return self.cells[location]

    def convert_cell_location_to_position(self, cell_location):
        """Convert a 2d coordinate into a 1d position by going through cols row by row"""
        row_idx, col_idx = cell_location
        position = row_idx * self.num_cols + col_idx
        return position

    def convert_position_to_cell_location(self, position):
        return position / self.num_cols, position % self.num_cols

    def encode_cell_state(self, cell_states):
        encoded_state = [NO_SYMBOL] * (self.num_rows * self.num_cols)
        for location, state in cell_states:
            encoded_state[self.convert_cell_location_to_position(location)] = state
        return tuple(encoded_state)

    def get_board_state(self):
        return [(location, cell.state) for location, cell in self.cells.iteritems()]
        #return self.cells.iteritems()

    def get_winning_state(self):
        for cell in self.cells.values():
            if cell.state == NO_SYMBOL:
                continue
            if cell.get_max_of_downstream_neighbors() + 1 >= self.num_connects_to_win:
                return cell.state
        return NO_SYMBOL

    def set_cell_state(self, location, state):
        if location not in self.cells:
            raise ValueError("No cell at position ({}, {}) on the game board".format(*location))
        self.cells[location].state = state
        if state != NO_SYMBOL:
            self.available_positions.remove(self.convert_cell_location_to_position(location))

    def get_available_game_positions(self):
        return self.available_positions

    def reset(self):
        self.available_positions = set()
        for location, cell in self.cells.iteritems():
            self.available_positions.add(self.convert_cell_location_to_position(location))
            cell.reset()


class Game:
    MIN_NUM_PLAYERS = 2
    MAX_NUM_PLAYERS = 2

    def __init__(self, players, num_rows, num_cols, num_connects_to_win):
        if len(players) < self.MIN_NUM_PLAYERS or len(players) > self.MAX_NUM_PLAYERS:
            raise GameError("Invalid number of players {}".format(str(len(players))))

        self.game_board = GameBoard(num_rows, num_cols, num_connects_to_win)
        self.next_player_index = 0
        self.players = players

    def play(self):
        """The main play loop of the model"""
        while not self.is_terminated():
            try:
                next_player = self.get_next_player()
                move = next_player.get_next_move(self.game_board.encode_cell_state(self.get_game_board_state()))
                if move is None:
                    # if no move available just skip
                    time.sleep(0.1)
                    continue
                self.make_move(self.next_player_index, move)
                self.print_game_board()
                time.sleep(1)
            except GameError as e:
                print(e.msg)
        self.print_winner()

    def get_game_board_state(self):
        return self.game_board.get_board_state()

    def get_next_player(self):
        """Returns the player whose turn is next"""
        if self.next_player_index < 0 or self.next_player_index >= len(self.players):
            raise GameError("Invalid next player index of {}".format(str(len(self.players))))
        return self.players[self.next_player_index]

    def get_last_player(self):
        return self.players[(self.next_player_index - 1) % len(self.players)]

    def get_winner(self):
        winner = self.game_board.get_winning_state()
        if winner != NO_SYMBOL:
            return self.get_last_player()
        return None

    def is_terminated(self):
        """Returns true if the one of the players has won the model"""
        # Game is over if X or O wins
        winner = self.game_board.get_winning_state()
        if winner != NO_SYMBOL:
            return True
        if len(self.game_board.get_available_game_positions()) > 0:
            return False
        # it is a draw then
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
        if self.game_board.get_cell(location).state != NO_SYMBOL:
            raise GameError("Board location of ({}, {}) is already occupied!".format(*location))

        # actually make the move by changing the state of the target cell
        self.game_board.set_cell_state(location, symbol)

        # switch to the next player
        self.next_player_index = (self.next_player_index + 1) % len(self.players)

    def print_game_board(self):
        print("=========" * self.game_board.num_cols)
        print(('--------' * self.game_board.num_cols + '\n').join(['|{:^6s}|' * self.game_board.num_cols + '\n']
                                                                  * self.game_board.num_rows)
              .format(*[str(self.game_board.get_cell((i, j)).state)
                        for i in range(self.game_board.num_rows)
                        for j in range(self.game_board.num_cols)]))
        print("=========" * self.game_board.num_cols)

    def print_winner(self):
        winner = self.get_winner()
        if winner is None:
            print("It is a draw")
        else:
            print("{} wins!".format(winner.get_id()))


if __name__ == '__main__':
    from player import RandomPlayer, PlayerType

    players = [RandomPlayer("Random Player 1", PlayerType.MaxPlayer),
               RandomPlayer("Random Player 2", PlayerType.MinPlayer)]
    g = Game(players, 3, 3, 3)
    for player in players:
        player.set_game(g.game_board)
    g.play()
