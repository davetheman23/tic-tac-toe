
class Cell:
    def __init__(self, row_id, col_id, size, left=0, top=0,):
        self.row_id = row_id
        self.col_id = col_id
        self.size = size
        self.left = left
        self.top = top
        self.center = self.get_center()

    def get_center(self):
        return self.left + self.size / 2, self.top + self.size / 2

    def get_bound(self, scale=1):
        scaled_size = self.size * scale
        return self.center[0] - scaled_size / 2, self.center[1] - scaled_size / 2, scaled_size, scaled_size

    def contains(self, pos_x, pos_y):
        return self.left < pos_x < self.left + self.size and self.top < pos_y < self.top + self.size


class Board:
    def __init__(self, cell_size, num_rows, num_cols, left=0, top=0, margin=5):
        self.left = left
        self.top = top
        self.margin = margin
        self.cells = [Cell(i, j, cell_size, left + margin + j * cell_size, top + margin + i * cell_size)
                      for i in range(num_rows) for j in range(num_cols)]

    def get_all_cells(self):
        return self.cells

    def get_board_cell(self, pos_x, pos_y):
        for cell in self.cells:
            if cell.contains(pos_x, pos_y):
                return cell
        # if we cannot find any cells, we just return None
        return None
