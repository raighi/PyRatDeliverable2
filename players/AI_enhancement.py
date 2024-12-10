# Imports
from typing import *
import json
import random
from pyrat import GameMode
from pyrat import Game, PlayerSkin, StartingLocation

# Import the players
from AI import AI
from Random4 import Random4


# Maze parameters
WIDTH = 25
HEIGHT = 20
CHEESE_NUMBER = 41
PLAYER_NUMBER = 2

# The weight of all edges, the coordinate and score of each player, and the coordinate of the cheeses
ENTRANCE_DIM = 2*WIDTH*HEIGHT - (WIDTH + HEIGHT) + 2*PLAYER_NUMBER + CHEESE_NUMBER

# Neural network parameters
LAYER_NUMBER = 5
NEURON = [ENTRANCE_DIM, 128, 64, 64, 4]

# Rewards rate
REWARDS = {"victory": 1000000, "score": 10000, "turn": -1}

# Genetic algorithm parameters
RANDOM_MUTATION = lambda x: x + random.uniform(-5, 5)
CHILD_PER_GENERATION = 20
GAME_PER_CHILD = 10
GENERATION_NUMBER = 100

# Customize the game parameters
CONFIG = {"cell_percentage": 80.0,
          "wall_percentage": 60.0,
          "mud_percentage": 20.0,
          "mud_range": [4,9],
          "nb_cheese": CHEESE_NUMBER,     
          "maze_width": WIDTH,
          "maze_height": HEIGHT,
          "game_mode": GameMode.SIMULATION}  

def initialize_weights():
    """
        This method initializes the weights.
        weights[layer][column][row]
        In:
            * None.
        Out:
            * weights: The initialized weights.
    """
    weights = []
    for i in range(LAYER_NUMBER-1):
        layer = []
        for j in range(NEURON[i]):
            neuron = []
            for k in range(NEURON[i+1]):
                neuron.append(0)
            layer.append(neuron)
        weights.append(layer)
    return weights

def initialize_bias():
    """
        This method initializes the bias.
        bias[layer][row]
        In:
            * None.
        Out:
            * bias: The initialized bias.
    """
    bias = []
    for i in range(LAYER_NUMBER-1):
        layer = []
        for j in range(NEURON[i+1]):
            layer.append(0)
        bias.append(layer)
    return bias

def initialize_network():
    """
        This method initializes the network.
        In:
            * None.
        Out:
            * weights: The initialized weights.
            * bias: The initialized bias.
    """
    weights = initialize_weights()
    bias = initialize_bias()
    return weights, bias

def reward_calcul(REWARDS: Dict, score: Tuple[int, int], turn: int) -> int:
    """
        This method computes the reward of the player.
        In:
            * REWARDS: The rewards rate.
            * score: The score of the player.
            * turn: The number of turns played.
        Out:
            * reward: The reward of the player.
    """

    victory = score[0] - score[1] > 0
    return victory*REWARDS["victory"] + score[0]*REWARDS["score"] + turn*REWARDS["turn"]

def forward_propagation(entrance: list[int],
                            weights: list[list[list[int]]],
                            bias: list[list[int]]
                            ) -> list[int]:
        """
            This method computes the output of the neural network.
            In:
                * entrance: The entrance of the neural network.
                * weights: The weights of the neural network.
                * bias: The bias of the neural network.
            Out:
                * output: The output of the neural network.
        """
        output = entrance
        for i in range(LAYER_NUMBER-1):
            new_output = []
            for j in range(NEURON[i+1]):
                neuron = 0
                for k in range(NEURON[i]):
                    neuron += output[k]*weights[i][k][j]
                neuron += bias[i][j]
                new_output.append(neuron)
            output = new_output
        return output

def network_mutation(network: Tuple[list[list[list[int]]], list[list[int]]],
                        random_mutation: Callable[[int], int]
                        ) -> Tuple[list[list[list[int]]], list[list[int]]]:
        """
            This method create a new network by mutating the old one.
            In:
                * network: The network to mutate.
                * random_mutation: The random mutation function.
            Out:
                * new_network: The new network.
        """
        new_network = ([], [])
        for i in range(LAYER_NUMBER-1):
            new_layer = []
            for j in range(NEURON[i]):
                new_neuron = []
                for k in range(NEURON[i+1]):
                    new_neuron.append(random_mutation(network[0][i][j][k]))
                new_layer.append(new_neuron)
            new_network[0].append(new_layer)

            new_bias = []
            for j in range(NEURON[i+1]):
                new_bias.append(random_mutation(network[1][i][j]))
            new_network[1].append(new_bias)

        return new_network

if __name__ == '__main__':
    INITIALIZE_NEED = False

    if INITIALIZE_NEED:
        # The current network defining the player
        current_network = initialize_network()

        # Save the current network
        with open('utils/current_network.json', 'w') as f:
            json.dump(current_network, f)
    
    else:
        # Load the saved network
        with open('utils/412925.0_43save.json', 'r') as f:
            current_network = json.load(f)


    for generation in range(GENERATION_NUMBER):
        # Create the children networks
        children_networks = []
        for i in range(CHILD_PER_GENERATION):
            children_networks.append(network_mutation(current_network, RANDOM_MUTATION))

        # Select the best child network
        best_child_network = children_networks[0]
        best_child_reward = float('-inf')
        for i in range(len(children_networks)):

            child_network = children_networks[i]

            with open('utils/current_network.json', 'w') as f:
                json.dump(child_network, f)

            reward = 0
            for j in range(GAME_PER_CHILD):

                # Instantiate a game with specified arguments
                game = Game(**CONFIG)

                # Instantiate players in distinct teams
                player_1 = AI(skin=PlayerSkin.RAT)
                player_2 = Random4(skin=PlayerSkin.PYTHON)
                game.add_player(player_1, "Team Ratz", location=StartingLocation.CENTER)
                game.add_player(player_2, "Team Pythonz", location=StartingLocation.CENTER)

                # Start the game and
                stats = game.start()

                score = (stats["players"]["AI"]["score"], stats["players"]["Random4"]["score"])
                reward += reward_calcul(REWARDS, score, stats["turns"])

                print("Game", j+1, "/", GAME_PER_CHILD)
                print("Score:", score)

            if reward > best_child_reward:
                best_child_reward = reward
                best_child_network = child_network

            print("Generation", generation +1, "/", GENERATION_NUMBER, "Child", i+1, "/", CHILD_PER_GENERATION)
            print("Reward:", reward)
            print("\n")

        # Update the current network
        current_network = best_child_network

        print("Generation", generation +1, "/", GENERATION_NUMBER, "done")
        print("Best reward:", best_child_reward)
        print("\n")

        # Save the current network
        with open('utils/'+str(best_child_reward)+'_2_'+str(generation +1)+'save.json', 'w') as f:
            json.dump(current_network, f)

    # Update the current network
    with open('utils/current_network.json', 'w') as f:
        json.dump(current_network, f)

    # Save the current network
    with open('utils/save.json', 'w') as f:
        json.dump(current_network, f)