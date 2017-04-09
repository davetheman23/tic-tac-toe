#!/usr/bin/env python

import pygame
import sys


class Visualizer:
    def __init__(self, simulator, human_player):
        self._simulator = simulator
        self._human_player = human_player

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

    def render(self):
        """Renders the current state of the game"""
        # next_player = self._simulator.get_next_player()
        next_player_id = -1

        # Display the next player
        text = self._font.render('Next player is ' + str(next_player_id), 1, (0, 0, 0))
        self._surface.blit(text, (0, 0, 100, 50))

        # Render the board
        for i in range(3):
            for j in range(3):
                pygame.draw.rect(self._surface, (0, 0, 0), (5 + j * 50, 55 + i * 50, 50, 50), 1)

    def handle_events(self, events):
        """Handles all events"""
        for event in events:
            if event.type is pygame.QUIT:
                pygame.quit()
                sys.exit()
