from pong import window
from pong import Paddle
from pong import Ball
import pygame

pygame.init()


class GameInformation:
    def __init__(self, hits, score):
        self.hits = hits
        self.score = score


class Game:
    win_size = (
        int(window.rect.width * window.enlarge),
        int(window.rect.height * window.enlarge))

    paddle_positions = {
        "left": [10, (window.rect.height // 2 - Paddle.height // 2)],
        "right": [
            (window.rect.width - 10 - Paddle.width), 
            (window.rect.height // 2 - Paddle.height // 2)
        ]
    }

    def __init__(self, color, training=True):
        # Initialize color
        self.color = color

        # Initialize paddle
        self.paddles = {
            "left": Paddle("normal", self.paddle_positions["left"]),
            # "left": Paddle("high", self.paddle_positions["left"]),
            "right": Paddle("high", self.paddle_positions["right"])
        }
        
        # Initialize ball
        self.ball = Ball(training)

        # Initialize game information
        self.hits = {
            "left": 0,
            "right": 0
        }
        self.score = {
            "left": 0,
            "right": 0
        }

    def draw_entities(self, win, display):
        for paddle in self.paddles.values():
            paddle.draw(display, self.color)
        self.ball.draw(display, self.color)

        resized_display = pygame.transform.scale(
            display, self.win_size)
        win.blit(resized_display, (0, 0))

    def loop(self, genomes, training=True):
        self.ball.update(self.paddles, self.hits, genomes, training)

        # Win check
        if self.ball.rect.centerx <= window.playable_rect.left:
            self.score["right"] += 1
            self.ball.round_reset(training)
        elif self.ball.rect.centerx >= window.playable_rect.right:
            self.score["left"] += 1
            self.ball.round_reset(training)

        # Game information
        game_info = GameInformation(
            self.hits, self.score)

        return game_info
