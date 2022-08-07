from pong import window
import pygame
import random
import math

pygame.init()


class Ball:
    # Ball size
    width = 10
    height = 10

    # Ball position
    original_x = (window.rect.w // 2 - width // 2)
    original_y = (window.rect.h // 2 - height // 2)

    # Movement
    max_vel = 5

    # Initialize -------------------------------------------------- #
    def __init__(self, training=True):
        # Rectangle
        self.rect = pygame.Rect(
            self.original_x, self.original_y, 
            self.width, self.height)

        # Velocities
        if training:
            angle = self.get_random_angle(-50, 50, [0])
            self.x_vel = abs(math.cos(angle) * self.max_vel) * random.choice([-1, 1])
            self.y_vel = math.sin(angle) * self.max_vel
        else:
            self.x_vel = self.max_vel
            self.y_vel = 0

    # Draw -------------------------------------------------------- #
    def draw(self, display, color):
        pygame.draw.rect(display, color, self.rect)

    # Update ------------------------------------------------------ #
    def update(self, paddle, hits, genomes, training):
        self.movement()
        self.paddle_collisions(paddle, hits, genomes, training)
        self.edge_collisions()

    def movement(self):
        self.rect.x += self.x_vel * window.delta_time
        self.rect.y += self.y_vel * window.delta_time

    def edge_collisions(self):
        handle_rect = self.rect.copy()
        handle_rect.x += self.x_vel * window.delta_time
        handle_rect.y += self.y_vel * window.delta_time
        if handle_rect.bottom >= window.playable_rect.bottom:
            self.rect.bottom = window.playable_rect.bottom
            # Update y velocity
            self.y_vel *= -1
        elif handle_rect.top <= window.playable_rect.top:
            self.rect.top = window.playable_rect.top

            # Update y velocity
            self.y_vel *= -1

    def paddle_collisions(self, paddles, hits, genomes, training):
        handle_rect = self.rect.copy()
        handle_rect.x += self.x_vel * window.delta_time
        handle_rect.y += self.y_vel * window.delta_time

        if self.x_vel < 0:  # ball is going LEFT
            if (handle_rect.centery >= paddles["left"].rect.top) and ( 
                handle_rect.centery <= paddles["left"].rect.bottom) and (
                handle_rect.left <= paddles["left"].rect.right):

                # Update x velocity
                self.x_vel *= -1

                # Update y velocity
                difference_in_y = paddles["left"].rect.centery - handle_rect.centery
                reduction_factor = (paddles["left"].rect.height / 2) / self.max_vel
                new_y_vel = difference_in_y / reduction_factor
                self.y_vel = -1 * new_y_vel

                # Encourage the higher the difference in Y between paddle and ball collision
                if training:
                    genomes[0].fitness += abs(difference_in_y)

                # Update hits
                hits["left"] += 1

        else:  # ball is going RIGHT
            if (handle_rect.centery >= paddles["right"].rect.top) and (
                handle_rect.centery <= paddles["right"].rect.bottom) and (
                handle_rect.right >= paddles["right"].rect.left):
            
                # Update x velocity
                self.x_vel *= -1

                # Update y velocity
                difference_in_y = paddles["right"].rect.centery - handle_rect.centery
                reduction_factor = (paddles["right"].rect.height / 2) / self.max_vel
                new_y_vel = difference_in_y / reduction_factor
                self.y_vel = -1 * new_y_vel

                # Update hits
                hits["right"] += 1

                # Encourage the higher the difference in Y between paddle and ball collision
                if training:
                    genomes[1].fitness += abs(difference_in_y)

    # Functions --------------------------------------------------- #
    def get_random_angle(self, min_angle, max_angle, excluded):
        angle = 0
        while angle in excluded:
            angle = math.radians(random.randrange(min_angle, max_angle))

        return angle

    def round_reset(self, training=True):
        # Rectangle
        self.rect.x = self.original_x
        self.rect.y = self.original_y

        # Velocities
        if training:
            angle = self.get_random_angle(-50, 50, [0])
            x_vel = abs(math.cos(angle) * self.max_vel)
            self.x_vel = x_vel if self.x_vel > 0 else -x_vel
            self.y_vel = math.sin(angle) * self.max_vel
        else:
            self.x_vel = self.max_vel
            self.y_vel = 0
