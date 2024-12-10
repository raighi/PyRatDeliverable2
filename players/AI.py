#####################################################################################################################################################
###################################################################### IMPORTS ######################################################################
#####################################################################################################################################################

# External imports
from typing import *
from typing_extensions import *
from numbers import *
import json

# PyRat imports
from pyrat import Player, Maze, GameState, Action


#####################################################################################################################################################
###################################################################### CLASSES ######################################################################
#####################################################################################################################################################

class AI (Player):

    """
        This player is an AI related to AI_enhancement.py, and needs this file to work.
        It works for dual player games.
    """

    #############################################################################################################################################
    #                                                                CONSTRUCTOR                                                                #
    #############################################################################################################################################

    def __init__ ( self:     Self,
                   *args:    Any,
                   **kwargs: Any
                 ) ->        Self:

        """
            This function is the constructor of the class.
            When an object is instantiated, this method is called to initialize the object.
            This is where you should define the attributes of the object and set their initial values.
            Arguments *args and **kwargs are used to pass arguments to the parent constructor.
            This is useful not to declare again all the parent's attributes in the child class.
            In:
                * self:   Reference to the current object.
                * args:   Arguments to pass to the parent constructor.
                * kwargs: Keyword arguments to pass to the parent constructor.
            Out:
                * A new instance of the class.
        """

        # Inherit from parent class
        super().__init__(*args, **kwargs)
       
    #############################################################################################################################################
    #                                                               PYRAT METHODS                                                               #
    #############################################################################################################################################

    @override
    def preprocessing ( self:       Self,
                        maze:       Maze,
                        game_state: GameState,
                      ) ->          None:
        
        """
            This method redefines the method of the parent class.
            It is called once at the beginning of the game.
            In:
                * self:       Reference to the current object.
                * maze:       An object representing the maze in which the player plays.
                * game_state: An object representing the state of the game.
            Out:
                * None.
        """
        # Use '../utils/current_network.json' for visualize
        with open('../utils/current_network.json', 'r') as f:
            self.network = json.load(f)

        self.weights = self.network[0]
        self.bias = self.network[1]

        self.LAYER_NUMBER = len(self.weights)+1
        self.NEURON = [len(self.weights[i]) for i in range(len(self.weights))]
        self.NEURON.append(len(self.weights[-1][0]))

        self.WIDTH = maze.width
        self.HEIGHT = maze.height
        self.INITIAL_CHEESE_NUMBER = len(game_state.cheese)

        self.DIRECTIONS = [Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST]
        
    #############################################################################################################################################

    @override
    def turn ( self:       Self,
               maze:       Maze,
               game_state: GameState,
             ) ->          Action:

        """
            This method redefines the abstract method of the parent class.
            It is called at each turn of the game.
            It returns an action to perform among the possible actions, defined in the Action enumeration.
            In:
                * self:       Reference to the current object.
                * maze:       An object representing the maze in which the player plays.
                * game_state: An object representing the state of the game.
            Out:
                * action: One of the possible actions.
        """
        directions = self.available_actions(maze, game_state)
        
        # If there is only one direction, skip the neural network
        if len(directions) == 1:
            return directions[0]
        
        else:
            # Get the entrance of the neural network
            entrance = self.get_entrance(maze, game_state)

            results = self.forward_propagation(entrance, self.weights, self.bias, game_state)

            # Get the index of the maximum value with available direction
            i_max = 0
            for i in range(1,len(results)):
                if self.DIRECTIONS[i] in directions:
                    if results[i] > results[i_max]:
                        i_max = i

            # Return an action
            return self.DIRECTIONS[i_max]

#############################################################################################################################################

    @override
    def postprocessing ( self:       Self,
                         maze:       Maze,
                         game_state: GameState,
                         stats:      Dict[str, Any],
                       ) ->          None:

        """
            This method redefines the method of the parent class.
            It is called once at the end of the game.
            In:
                * self:       Reference to the current object.
                * maze:       An object representing the maze in which the player plays.
                * game_state: An object representing the state of the game.
                * stats:      Statistics about the game.
            Out:
                * None.
        """

        ()

#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
##################################################################OTHER_METHODS######################################################################

    def forward_propagation(    self:       Self,
                                entrance:   list[int],
                                weights:    list[list[list[int]]],
                                bias:       list[list[int]],
                                game_state: GameState,
                                ) ->        list[int]:
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
            for i in range(self.LAYER_NUMBER-1):
                new_output = []
                for j in range(self.NEURON[i+1]):
                    neuron = 0
                    # If it is the first layer, don't take in count the cheeses already eaten
                    cheese_difference = 0
                    if i == 0:
                        cheese_difference = self.INITIAL_CHEESE_NUMBER - len(game_state.cheese)
                    for k in range(self.NEURON[i] - cheese_difference):
                        neuron += output[k]*weights[i][k][j]
                        
                    neuron += bias[i][j]
                    new_output.append(neuron)
                output = new_output
            return output

    def edge_to_entrance_index( self: Self,
                                edge: Tuple[int, int]
                                ) -> int:
        """
           This method converts an edge to an index in the entrance of the neural network.
           In:
               * edge: The edge to convert.
           Out:
               * index: The index in the entrance of the neural network.
        """
        x, y = edge
        row = x // self.WIDTH

        return row * (2*self.WIDTH - 1) + x%self.WIDTH + y-x-1


    def get_entrance(   self:       Self,
                        maze:       Maze,
                        game_state: GameState
                        ) ->        list[int]:
            """
                This method gets the entrance of the neural network.
                In:
                    * maze: The maze of the game.
                    * game_state: The state of the game.
                Out:
                    * entrance: The entrance of the neural network.
            """
            entrance = [0 for _ in range( 2*self.WIDTH*self.HEIGHT - (self.WIDTH + self.HEIGHT) )]

            # Add edges states
            for edge in maze.edges:
                entrance[self.edge_to_entrance_index(edge)] = maze.get_weight(edge[0], edge[1])

            # Add players states
            entrance.append(game_state.score_per_player[self.name])
            entrance.append(game_state.player_locations[self.name])
            for player in game_state.score_per_player:
                if player != self.name:
                    entrance.append(game_state.score_per_player[player])
                    entrance.append(game_state.player_locations[player])

            # Add cheeses states
            for cheese in game_state.cheese:
                entrance.append(cheese)

            return entrance
    
    def available_actions(self: Self, maze: Maze, game_state: GameState) -> List[Action]:
        """
            This method returns the list of available actions.
            In:
                * maze: The maze of the game.
                * game_state: The state of the game.
            Out:
                * actions: The list of available actions.
        """
        neighbors = maze.get_neighbors(game_state.player_locations[self.name])
        actions = []
        for neighbor in neighbors:
            actions.append(maze.locations_to_action(game_state.player_locations[self.name], neighbor))
        return actions