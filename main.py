from pong import Game
from pong import window
from datetime import datetime
import pygame
import json
import sys
import os
import pickle
import neat


class PongGame:
    def __init__(self, win, display, clock):
        self.win = win
        self.display = display
        self.clock = clock

    # Testing ----------------------------------------------------- #
    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game([255, 255, 255], training=False)

        # Loop
        run = True
        while run:
            window.update_deltatime(False)

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            paddles = game.paddles
            ball = game.ball

            # Player movement
            keys = pygame.key.get_pressed()
            paddles["left"].testing_movement(
                keys[pygame.K_w], keys[pygame.K_s])

            # Get input
            inputs = (
                paddles["right"].rect.y,  # Y coordinate of the paddle
                ball.rect.y,  # Y coordinate of the ball
                abs(paddles["right"].rect.x - ball.rect.x),  # Distance in the X coordinate between the ball and the paddle
            )

            # Get output
            output = net.activate(inputs)

            # Decisions
            decision = output.index(max(output))
            if decision == 1:  # move up
                game.paddles["right"].testing_movement(True, False)
            elif decision == 2:  # move down
                game.paddles["right"].testing_movement(False, True)

            # Game loop
            game.loop(None, training=False)

            # Draw
            self.display.fill(window.white)
            window.draw_playablesurface(self.display)
            window.draw_centerline(self.display)

            game.draw_entities(self.win, self.display)

            pygame.display.update() 

            # Update clock
            self.clock.tick(window.testing_framerate)

        pygame.quit()
        sys.exit()

    # Training ---------------------------------------------------- #
    def train_ai(self, genome1, other_genomes, config):
        grounds = []
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        for ((_, genome2), color) in zip(other_genomes, colors):
            net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
            ground = {
                "nets": [net1, net2], 
                "game": Game(color),
                "dead": False
            }
            
            grounds.append(ground)

        # Loop
        run = True
        while run:
            # Update deltatime
            window.update_deltatime()

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            # Train
            for ground in grounds:
                if not ground["dead"]:
                    # Paddle movement
                    genomes = [genome1, genome2]
                    self.paddle_movement(
                        ground["nets"], genomes, ground["game"])

                    # Run game
                    game_info = ground["game"].loop(genomes)

                    # End training after a genome has scored
                    if game_info.score["left"] >= 1:
                        ground["dead"] = True
                    elif game_info.score["right"] >= 1:
                        ground["dead"] = True
                    
                    # End training after hits exceeded 50
                    if game_info.hits["left"] > 50:
                        ground["dead"] = True

            # Draw
            self.draw(grounds)

            # Update clock
            self.clock.tick(window.training_framerate)

            # Get number or dead genomes
            num_of_dead = 0
            for ground in grounds:
                if ground["dead"]:
                    num_of_dead += 1

            # End loop if all genomes are daed
            if len(grounds) <= num_of_dead:
                run = False

        return False

    def paddle_movement(self, nets, genomes, game):
        # Paddle movement
        for paddle, net, genome in zip(game.paddles.values(), nets, genomes):
            # Get inputs
            input = (
                paddle.rect.y,  # Y coordinate of the paddle
                game.ball.rect.y,  # Y coordinate of the ball
                abs(paddle.rect.x - game.ball.rect.x)  # Distance in the X coordinate between the ball and the paddle
            )

            # Get output
            output = net.activate(input)

            # Decisions
            decision = output.index(max(output))
            if decision == 0:  # don't move
                genome.fitness -= 0.01  # we want to discourage not moving
            if decision == 1:  # move up
                paddle.training_movement(True, False, genome)
            elif decision == 2:  # move down
                paddle.training_movement(False, True, genome)

    def draw(self, grounds):
        # Draw background
        self.display.fill(window.white)
        window.draw_playablesurface(self.display)
        window.draw_centerline(self.display)

        # Draw entities
        for ground in grounds:
            if not ground["dead"]:
                ground["game"].draw_entities(self.win, self.display)

        # Update display
        pygame.display.update()


def eval_genomes(genomes, config):
    # Initialize window
    win = pygame.display.set_mode(Game.win_size, 32)
    display = pygame.Surface(window.rect.size)
    clock = pygame.time.Clock()

    # Print time
    print(datetime.now())
    
    # Run each genome against each other one time to determine the fitness
    for idx, (_, genome1) in enumerate(genomes):
        # Pop current genome in other genomes
        other_genomes = genomes.copy()
        other_genomes.pop(idx)

        # Set fitness to zero
        genome1.fitness = 0 if genome1.fitness == None else genome1.fitness
        for (_, genome2) in other_genomes:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness

        # Train
        game = PongGame(win, display, clock)
        force_quit = game.train_ai(genome1, other_genomes, config)
        if force_quit:
            quit()


def run_neat(config):
    # population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-75") 
    population = neat.Population(config)
    stats = neat.StatisticsReporter()
    num_generations = 1

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(1))

    # Dump the best to a pickle file
    winner = population.run(eval_genomes, num_generations)
    with open("best.pickle", "wb") as pickle_file:
        pickle.dump(winner, pickle_file)


def test_ai(config):
    with open("checkpoints/best.pickle", "rb") as pickle_file:
        winner = pickle.load(pickle_file)

    # Initialize window
    win = pygame.display.set_mode(Game.win_size, 32)
    display = pygame.Surface(window.rect.size)
    clock = pygame.time.Clock()

    # Test ai
    game = PongGame(win, display, clock)
    game.test_ai(winner, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)

    # Config file
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation,
        config_path
    )
    
    # JSON file of colors
    json_path = os.path.join(local_dir, "colors.json")
    with open(json_path) as json_file:
        colors = json.load(json_file)
        colors.reverse

    # run_neat(config)
    test_ai(config) 
