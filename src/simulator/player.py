#!/usr/bin/env python

import random


class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    def get_next_move(self, state):
        return None


class RandomPlayer(Player):
    def __init__(self, player_id):
        Player.__init__(self, player_id)

    def get_next_move(self, state):
        move = (random.randint(0, 2),
                random.randint(0, 2))
        return move
