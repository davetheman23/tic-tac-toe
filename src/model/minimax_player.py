#!/usr/bin/env python

import player
import copy


class MinimaxPlayer(player.Player):
    NONE = 0
    X = 1
    O = -1

    def __init__(self, player_id):
        player.Player.__init__(self, player_id, player.PlayerType.MaxPlayer)

        self.v = {}

        print("Initializing minimax player...")
        s = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.max_value(s)
        print("...done (computed {} values)".format(str(len(self.v))))

    def get_next_move(self, state):
        s = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        for k in range(len(state)):
            # i, j = self.game_board.convert_position_to_cell_location(k)
            i, j = k / 3, k % 3
            s[i][j] = state[k]

        # TODO hacky
        next_state = self.minimax_decision(s)
        for i in range(3):
            for j in range(3):
                if s[i][j] != next_state[i][j]:
                    # print("Minimax player placing X at ({ii}, {jj})...".format(ii=str(i),
                    #                                                            jj=str(j)))
                    return i, j

        print("Error in minimax player!")
        return 0, 0

    def num_to_state(self, num):
        state = [[self.NONE for i in range(3)] for j in range(3)]

        for i in range(3):
            for j in range(3):
                k = i * 3 + j

                # kth bit indicates if the cell is filled
                if num & (1 << k):
                    # (k + 9)th bit indicates if the cell is an X or an O
                    if num & (1 << (k + 9)):
                        state[i][j] = self.X
                    else:
                        state[i][j] = self.O

        return state

    def state_to_num(self, state):
        num = 0

        for i in range(3):
            for j in range(3):
                k = i * 3 + j

                if state[i][j] != self.NONE:
                    # Set the kth bit to indicate that the cell is filled
                    num = num | (1 << k)
                    # print(str(num))

                    if state[i][j] == self.X:
                        num = num | (1 << (k + 9))

        return num

    @staticmethod
    def is_terminal(state):
        # Compute the row, column, and diagonal sums
        row_sums = map(sum, state)
        col_sums = map(sum, [list(column) for column in zip(*state)])
        left_diag_sum = 0
        right_diag_sum = 0

        for i in range(3):
            left_diag_sum += state[i][i]
            right_diag_sum += state[i][2 - i]

        # print("left_diag_sum = {}".format(str(left_diag_sum)))
        # print("right_diag_sum = {}".format(str(right_diag_sum)))

        # Check if a player has won on the diagonal
        if left_diag_sum == 3 * MinimaxPlayer.X or right_diag_sum == 3 * MinimaxPlayer.X:
            # print("X player wins!")
            return True, +1
        elif left_diag_sum == 3 * MinimaxPlayer.O or right_diag_sum == 3 * MinimaxPlayer.O:
            # print("O player wins!")
            return True, -1

        # The row/column sums indicate if a player has won along a row or column
        for s in (row_sums + col_sums):
            if s == 3 * MinimaxPlayer.X:
                # print("X player wins!")
                return True, +1
            elif s == 3 * MinimaxPlayer.O:
                # print("O player wins!")
                return True, -1

        # Check if it is not a terminal state yet
        for i in range(3):
            for j in range(3):
                if state[i][j] == MinimaxPlayer.NONE:
                    return False, 0

        # Otherwise, there is draw
        return True, 0

    def get_children(self, state, symbol):
        children = []

        for i in range(3):
            for j in range(3):
                if state[i][j] == self.NONE:
                    # print("Adding child with {sym} at ({row}, {col})".format(sym=str(symbol),
                    #                                                          row=str(i),
                    #                                                          col=str(j)))
                    child = copy.deepcopy(state)
                    child[i][j] = symbol
                    children.append(child)

        return children

    def max_value(self, state):
        terminal, utility = self.is_terminal(state)
        if terminal:
            return utility
        
        i = self.state_to_num(state)
        if i in self.v:
            return self.v[i]

        v = -1000
        for c in self.get_children(state, self.X):
            v = max(v, self.min_value(c))

        self.v[i] = v
        return v

    def min_value(self, state):
        terminal, utility = self.is_terminal(state)
        if terminal:
            return utility

        i = self.state_to_num(state)
        if i in self.v:
            return self.v[i]

        v = 1000
        for c in self.get_children(state, self.O):
            v = min(v, self.max_value(c))

        self.v[i] = v
        return v

    def minimax_decision(self, state):
        best_child = None
        best_min = -1000
        for c in self.get_children(state, self.X):
            m = self.min_value(c)
            if m > best_min:
                best_min = m
                best_child = c

        return best_child

if __name__ == '__main__':
    p = MinimaxPlayer(0)

    s = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]

    print("Solving for minimax values...")
    v_start = p.max_value(s)
    print("...done!")

    s_test = [[1, 1, -1],
              [0, -1, 0],
              [0, 0, 0]]
    print("At board {}...".format(str(s_test)))
    best_child = p.minimax_decision(s_test)
    print("next board {}".format(str(best_child)))

    s_term = [[1, 1, -1], [1, -1, 0], [-1, 0, 0]]
    terminal, utility = p.is_terminal(s_term)
    print(str(s_term))
    print(str(terminal))
    print(str(utility))
