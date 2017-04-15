#!/usr/bin/env python

import pygame
import sys
import time

from board import Board, Cell
from model.player import HumanPlayer

COLOR_BLACK = pygame.Color("Black")
COLOR_WHITE = pygame.Color("White")


class Visualizer:
    def __init__(self, game):
        self.game = game
        self.board = Board(60, game.game_board.num_rows, game.game_board.num_cols, 50, 50)

        pygame.init()

        self._surface = pygame.display.set_mode((400, 300))
        self._surface.fill(COLOR_WHITE)
        pygame.display.set_caption('Tic-Tac-Toe')

        self._font = pygame.font.SysFont('Arial', 28)
        if self._font is None:
            sys.exit('Error: could not load system font!')

    def run(self):
        """
        Contains the main run loop that updates visualizations and 
        handles events
        """
        while True:
            # Handle events
            self.handle_events(pygame.event.get())

            # get model state (currently not thread-safe)
            self.board.set_board_state(self.game.get_game_board_state())

            # Render the current state of the model
            self.render()

            # Update the display
            pygame.display.update()
            time.sleep(0.1)

    def render(self):
        """Renders the current state of the model"""
        current_player = self.game.get_next_player()

        # Display the current player
        self._surface.fill(COLOR_WHITE)
        text = self._font.render("Current player is {}".format(str(current_player.get_id())), 1, COLOR_BLACK)
        self._surface.blit(text, (0, 0, 100, 50))

        # Render the board
        for _, cell in self.board.get_all_cells().iteritems():
            pygame.draw.rect(self._surface, COLOR_BLACK, cell.get_bound(), 1)
            if cell.get_state() == Cell.State.Nought:
                pygame.draw.circle(self._surface, COLOR_BLACK, cell.get_center(), int(cell.size / 2 * 0.7), 2)
            elif cell.get_state() == Cell.State.Cross:
                pygame.draw.line(self._surface, COLOR_BLACK, (cell.left, cell.top),
                                 (cell.left + cell.size, cell.top + cell.size))
                pygame.draw.line(self._surface, COLOR_BLACK, (cell.left, cell.top + cell.size),
                                 (cell.left + cell.size, cell.top))

    def handle_events(self, events):
        """Handles all events"""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up_event(*event.pos)

    def handle_mouse_button_up_event(self, pos_x, pos_y):
        cell = self.board.get_board_cell(pos_x, pos_y)
        if cell is not None and cell.get_state() == Cell.State.Unmarked:
            player = self.game.get_next_player()
            if isinstance(player, HumanPlayer):
                player.handle_mouse_up_event(cell.row_id, cell.col_id)
