from pong import Game
import pygame
import pickle
import neat
import sys
import os


class PongGame:
    def __init__(self):
        self.game = Game()

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
            self.game.draw()
            self.game.update_clock()
            pygame.display.update()

            print(game_info.score["left"], game_info.score["right"])

        pygame.quit()
        sys.exit()

    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        # Loop
        run = True
        while run:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            paddles = self.game.paddles
            ball = self.game.ball

            # Get inputs
            inputs1 = (
                paddles["left"].rect.y,  # Y coordinate of the paddle
                ball.rect.y,  # Y coordinate of the ball
                abs(paddles["left"].rect.x - ball.rect.x),  # Distance in the X coordinate between the ball and the padle
            )
            inputs2 = (
                paddles["right"].rect.y,  # Y coordinate of the paddle
                ball.rect.y,  # Y coordinate of the ball
                abs(paddles["right"].rect.x - ball.rect.x),  # Distance in the X coordinate between the ball and the padle
            )

            # Get outputs
            output1 = net1.activate(inputs1)
            output2 = net2.activate(inputs2)

            # Decisions
            decision1 = output1.index(max(output1))
            if decision1 == 1:  # move up
                self.game.paddles["left"].movement(True, False)
            elif decision1 == 2:  # move down
                self.game.paddles["left"].movement(False, True)

            decision2 = output2.index(max(output2))
            if decision2 == 1:  # move up
                self.game.paddles["right"].movement(True, False)
            elif decision2 == 2:  # move down
                self.game.paddles["right"].movement(False, True)

            # Run game
            game_info = self.game.loop()
            self.game.draw()
            pygame.display.update()

            # Break loop after a paddle has scored
            if game_info.score["left"] >= 1 or game_info.score["right"] >= 1 or (
                    game_info.hits["left"] > 50):
                self.calculate_fitness(genome1, genome2, game_info)
                run = False

        return False

    def calculate_fitness(self, genome1, genome2, game_info):
        genome1.fitness += game_info.hits["left"]
        genome2.fitness += game_info.hits["right"]


def eval_genomes(genomes, config):
    for idx, (_, genome1) in enumerate(genomes):
        if idx == len(genomes) - 1:
            break

        genome1.fitness = 0
        for _, genome2 in genomes[idx+1:]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            
            game = PongGame()
            force_quit = game.train_ai(genome1, genome2, config)
            if force_quit:
                quit()


def run_neat(config):
    # population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-1")
    population = neat.Population(config)
    stats = neat.StatisticsReporter()

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(1))

    # Dump the best to a pickle file
    winner = population.run(eval_genomes, 250)
    with open("best.pickle", "wb") as pickle_file:
        pickle.dump(winner, pickle_file)


def test_ai(config):
    with open("best.pickle", "wb") as pickle_file:
        winner = pickle.load(pickle_file)

    game = PongGame()
    game.test_ai(winner, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation,
        config_path
    )

    run_neat(config)
    # test_ai(config)
