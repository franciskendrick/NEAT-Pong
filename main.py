from pong import Game
from pong import window
import pygame
import json
import sys
import os
import pickle
import neat


class PongGame:
    def __init__(self, window, display, clock):
        self.win = window
        self.display = display
        self.clock = clock

    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Loop
        run = True
        while run:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            paddles = self.game.paddles
            ball = self.game.ball

            # Get input
            inputs = (
                paddles["right"].rect.y,  # Y coordinate of the paddle
                ball.rect.y,  # Y coordinate of the ball
                abs(paddles["right"].rect.x - ball.rect.x),  # Distance in the X coordinate between the ball and the padle
            )

            # Get output
            output = net.activate(inputs)

            # Decisions
            decision = output.index(max(output))
            if decision == 1:  # move up
                self.game.paddles["right"].movement(True, False)
            elif decision == 2:  # move down
                self.game.paddles["right"].movement(False, True)

            game_info = self.game.loop()
            self.game.draw_background()
            self.game.draw_entities()
            pygame.display.update()
            
            self.game.clock.tick(window.framerate)

            print(game_info.score["left"], game_info.score["right"])

        pygame.quit()
        sys.exit()

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
            for idx, ground in enumerate(grounds):
                if not ground["dead"]:
                    # Paddle movement
                    genomes = [genome1, genome2]
                    self.paddle_movement(
                        ground["nets"], genomes, ground["game"])

                    # Run game
                    game_info = ground["game"].loop()

                    # End training loop after a genomes has scored
                    if game_info.score["left"] >= 1:
                        genome2.fitness -= 25
                        self.calculate_fitness(genome1, genome2, game_info)
                        ground["dead"] = True
                    elif game_info.score["right"] >= 1:
                        genome1.fitness -= 25
                        self.calculate_fitness(genome1, genome2, game_info)
                        ground["dead"] = True
                    
                    # End training after hits exceeded 50
                    if game_info.hits["left"] > 50:
                        self.calculate_fitness(genome1, genome2, game_info)
                        grounds[idx]["dead"] = True



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

            # Update clock
            self.clock.tick(window.framerate)



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
        paddles = game.paddles
        ball = game.ball

        # Paddle movement
        sides = ["left", "right"]
        for side, net, genome in zip(sides, nets, genomes):
            # Get inputs
            input = (
                paddles[side].rect.y,  # Y coordinate of the paddle
                ball.rect.y,  # Y coordinate of the ball
                abs(paddles[side].rect.x - ball.rect.x)  # Distance in the X coordinate between the ball and the paddle
            )

            # Get output
            output = net.activate(input)

            # Decisions
            decision = output.index(max(output))
            if decision == 0:  # don't move
                genome.fitness -= 0.05  # we want to discourage this
            if decision == 1:  # move up
                game.paddles[side].movement(True, False)
            elif decision == 2:  # move down
                game.paddles[side].movement(False, True)

    def calculate_fitness(self, genome1, genome2, game_info):
        genome1.fitness += game_info.sum_difference_in_y["left"]
        genome2.fitness += game_info.sum_difference_in_y["right"]


def eval_genomes(genomes, config):
    # Initialize window
    win = pygame.display.set_mode(Game.win_size, 32)
    display = pygame.Surface(window.rect.size)
    clock = pygame.time.Clock()
    
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
    # population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-24")
    population = neat.Population(config)
    stats = neat.StatisticsReporter()
    num_generations = 10

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(1))

    # Dump the best to a pickle file
    winner = population.run(eval_genomes, num_generations)
    with open("best.pickle", "wb") as pickle_file:
        pickle.dump(winner, pickle_file)


def test_ai(config):
    with open("best.pickle", "rb") as pickle_file:
        winner = pickle.load(pickle_file)

    game = PongGame()
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
    
    # JSON file
    json_path = os.path.join(local_dir, "colors.json")
    with open(json_path) as json_file:
        colors = json.load(json_file)

    run_neat(config)
    # test_ai(config)
