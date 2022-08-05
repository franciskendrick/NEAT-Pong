from pong import window
import pygame

pygame.init()


class Paddle:
    # Paddle size
    width = 5
    height = 50

    # Movement
    sens_to_vel_switchcase = {
        "low": 2,
        "normal": 4,
        "high": 6
    }

    # Initialize -------------------------------------------------- #
    def __init__(self, sensitivity, pos):
        self.vel = self.sens_to_vel_switchcase[sensitivity]
        self.rect = pygame.Rect(
            *pos, self.width, self.height)

    # Draw -------------------------------------------------------- #
    def draw(self, display):
        pygame.draw.rect(display, window.white, self.rect)

    # Update ------------------------------------------------------ #
    def movement(self, up, down):
        # Up movement
        if up:
            # Get a hitbox handle
            handle_hitbox = self.rect.copy()
            handle_hitbox.y -= self.vel
            # Check for playable rectangle and hitbox collision
            if window.playable_rect.top < handle_hitbox.top:
                self.rect.y -= self.vel

        # Down movement
        if down: 
            # Get a hitbox handle
            handle_hitbox = self.rect.copy()
            handle_hitbox.y += self.vel
            # Check for playable rectangle and hitbox collision
            if window.playable_rect.bottom > handle_hitbox.bottom:
                self.rect.y += self.vel

    # Functions --------------------------------------------------- #
    def update_sensitivity(self, sensitivity):
        self.vel = self.sens_to_vel_switchcase[sensitivity]
