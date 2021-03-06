from enum import Enum

from model.game import NO_SYMBOL, X_SYMBOL, O_SYMBOL

class Cell:
    class State(Enum):
        Cross = "cross"
        Nought = "nought"
        Unmarked = "unmarked"

    def __init__(self, row_id, col_id, size, left=0, top=0,):
        self.row_id = row_id
        self.col_id = col_id
        self.size = size
        self.left = left
        self.top = top
        self.center = self.left + self.size / 2, self.top + self.size / 2
        self.state = Cell.State.Unmarked

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_bound(self):
        return self.left, self.top, self.size, self.size

    def get_state(self):
        return self.state

    def contains(self, pos_x, pos_y):
        return self.left < pos_x < self.left + self.size and self.top < pos_y < self.top + self.size

    def set_state(self, content):
        """Set the cell with state (cross, nought or unmarked) unconditionally"""

        if not isinstance(content, Cell.State):
            raise ValueError("Can only mark cell with '{}' type".format(type(Cell.State())))
        self.state = content


class Board:
    def __init__(self, cell_size, num_rows, num_cols, left=0, top=0, margin=5):
        self.left = left
        self.top = top
        self.margin = margin
        self.cells = {(i, j): Cell(i, j, cell_size, left + margin + j * cell_size, top + margin + i * cell_size)
                      for i in range(num_rows) for j in range(num_cols)}

    def get_all_cells(self):
        return self.cells

    def get_board_cell(self, pos_x, pos_y):
        for pos, cell in self.cells.iteritems():
            if cell.contains(pos_x, pos_y):
                return cell
        # if we cannot find any cells, we just return None
        return None

    def set_board_state(self, board_state):
        for location, state in board_state:
            if state == NO_SYMBOL:
                self.cells[location].set_state(Cell.State.Unmarked)
            elif state == X_SYMBOL:
                self.cells[location].set_state(Cell.State.Cross)
            elif state == O_SYMBOL:
                self.cells[location].set_state(Cell.State.Nought)
            else:
                raise ValueError("State '{}' not recognized!".format(str(state)))
