from pong import window
from pong import Paddle
from pong import Ball
import pygame

pygame.init()


class GameInformation:
    def __init__(self, hits, score, sum_difference_in_y):
        self.hits = hits
        self.score = score
        self.sum_difference_in_y = sum_difference_in_y


class Game:
    win_size = (
        int(window.rect.width * window.enlarge),
        int(window.rect.height * window.enlarge))

    def __init__(self):
        # Initialize window
        self.win = pygame.display.set_mode(self.win_size, 32)
        self.display = pygame.Surface(window.rect.size)
        self.clock = pygame.time.Clock()

        # Initialize paddle
        self.paddles = {
            "left": Paddle(
                "normal", 
                [10, (window.rect.height // 2 - Paddle.height // 2)]
            ),
            "right": Paddle(
                "normal", [
                    (window.rect.width - 10 - Paddle.width), 
                    (window.rect.height // 2 - Paddle.height // 2)
                ]
            )
        }
        
        # Initialize ball
        self.ball = Ball()

        # Initialize game information
        self.hits = {
            "left": 0,
            "right": 0
        }
        self.score = {
            "left": 0,
            "right": 0
        }
        self.sum_difference_in_y = {
            "left": 0,
            "right": 0
        }

    def draw(self):
        self.display.fill(window.white)
        window.draw_playablesurface(self.display)
        window.draw_centerline(self.display)

        for paddle in self.paddles.values():
            paddle.draw(self.display)
        self.ball.draw(self.display)
        
        resized_display = pygame.transform.scale(
            self.display, self.win_size)
        self.win.blit(resized_display, (0, 0))

    def loop(self):
        # Update
        keys = pygame.key.get_pressed()
        self.paddles["left"].movement(
            keys[pygame.K_w], keys[pygame.K_s])
        self.paddles["right"].movement(
            keys[pygame.K_UP], keys[pygame.K_DOWN])

        side, difference_in_y = self.ball.update(self.paddles, self.hits)
        if (side, difference_in_y) != (None, None):
            difference_in_y = abs(difference_in_y)
            self.sum_difference_in_y[side] += abs(difference_in_y)

        # Win check
        if self.ball.rect.left <= window.playable_rect.left:
            self.score["left"] += 1
            self.ball.round_reset()
        elif self.ball.rect.right >= window.playable_rect.right:
            self.score["right"] += 1
            self.ball.round_reset()

        # Game information
        game_info = GameInformation(
            self.hits, self.score, self.sum_difference_in_y)

        return game_info
