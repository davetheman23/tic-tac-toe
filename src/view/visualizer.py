#!/usr/bin/env python

import pygame
import sys
import time

from view.board import Board, Cell


class Visualizer:
    def __init__(self, simulator, human_player):
        self._simulator = simulator
        self._human_player = human_player

        self.board = Board(60, 3, 5, 50, 50)

        pygame.init()

        self._surface = pygame.display.set_mode((400, 300))
        self._surface.fill((255, 255, 255))
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
            # Render the current state of the game
            self.render()

            # Handle events
            self.handle_events(pygame.event.get())

            # Update the display
            pygame.display.update()
            time.sleep(0.01)

    def render(self):
        """Renders the current state of the game"""
        # next_player = self._simulator.get_next_player()
        next_player_id = -1

        # Display the next player
        text = self._font.render("Next player is {}".format(str(next_player_id)), 1, (0, 0, 0))
        self._surface.blit(text, (0, 0, 100, 50))

        # Render the board
        for cell in self.board.get_all_cells():
            pygame.draw.rect(self._surface, (0, 0, 0), cell.get_bound(0.99), 1)

    def handle_events(self, events):
        """Handles all events"""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up_event(*event.pos)

    def handle_mouse_button_up_event(self, pos_x, pos_y):
        text = "Not found"
        cell = self.board.get_board_cell(pos_x, pos_y)
        if cell is not None:
            text = "({}, {})".format(cell.row_id, cell.col_id)
            self._surface.blit(self._font.render(text, 1, (0, 0, 0)), cell.get_bound())
