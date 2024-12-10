#####################################################################################################################################################
######################################################################## INFO #######################################################################
#####################################################################################################################################################

"""
    This file contains useful elements to define a particular player.
    In order to use this player, you need to instanciate it and add it to a game.
    Please refer to example games to see how to do it properly.
"""

#####################################################################################################################################################
###################################################################### IMPORTS ######################################################################
#####################################################################################################################################################

# External imports
from typing import *
from typing_extensions import *
from numbers import *
from pyrat import Graph
import sys
import os
sys.path.append(os.path.join("..", "utils"))
from generalutils import simplify_graph

# PyRat imports
from pyrat import Player, Maze, GameState, Action

#####################################################################################################################################################
###################################################################### CLASSES ######################################################################
#####################################################################################################################################################

class Greedy (Player):

    """
        Greedy player with the heuristic of the nearest cheese.
        Heuristic :
        "Le chemin le plus court qui passe par tous les morceaux de fromage peut être approximé en 
        allant séquentiellement vers le morceau de fromage le plus proche"
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

        # Way to the next cheese
        self.way = []
        
    
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
        # Create the simplify graph with only the cheeses and the source
        # The "weight" of edges is a couple of the distance between the two vertices and the way between them
        self.simplified_graph = simplify_graph(maze, game_state.cheese, game_state.player_locations[self.name])

        
        # Find the greedy permutation
        self.greedy_permutation = self.find_greedy_permutation(game_state.cheese, game_state.player_locations[self.name])


        # Find the whole way
        self.way = self.permutation_to_way(self.greedy_permutation, self.simplified_graph)

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
        
        # Return an action
        action = self.find_next_action(maze, game_state)
        return action


    #############################################################################################################################################
    #                                                               OTHER METHODS                                                               #
    #############################################################################################################################################
    
    
    def find_next_action ( self:       Self,
                          maze:       Maze,
                          game_state: GameState,
                        ) ->          Action:
        """
           This method returns an action to perform among the possible actions, defined in the Action enumeration.
           Here, the action is chosen randomly among those that don't hit a wall, and that lead to an unvisited cell if possible.
           If no such action exists, we choose randomly among all possible actions that don't hit a wall.
           In:
               * self:       Reference to the current object.
               * maze:       An object representing the maze in which the player plays.
               * game_state: An object representing the state of the game.
           Out:
               * action: One of the possible actions.
        """

        # Find the next action from the way
        if self.way == []:
            action = Action.NOTHING
            print("no way")
        else:
            action = maze.locations_to_action(game_state.player_locations[self.name], self.way.pop(0))

        return action
    
#####################################################################################################################################################
#####################################################################################################################################################
    
    def permutation_to_way( self: Self,
                            permutation: List[Integral],
                            simplified_graph: Graph
                          ) -> List[Integral]:
        """
            This method returns the way that pass on all cheeses in the order of the permutation
            In:
                * permutation: The permutation.
                * simplified_graph: The simplified graph of cheeses and source.
            Out:
                * The way of the permutation.
        """

        way = []
        for i in range(1, len(permutation)):
            intermedaire_way = (simplified_graph[permutation[i-1]][permutation[i]]["way"])
            way += intermedaire_way
        return way
    
    def find_greedy_permutation( self: Self,
                                cheeses: List[Integral],
                                starting_vertexe: Integral
                              ) -> List[Integral]:
        """
            This method returns the greedy permutation of cheeses to visit.
            In:
                * cheeses : The list of cheeses.
                * starting_vertexe : The starting vertexe.
            Out:
                * The greedy permutation
        """
        is_visited_cheese = {cheese : False for cheese in cheeses}
        greedy_permutation = [starting_vertexe]

        for _ in range(len(cheeses)):
            best_cheese = min( (cheese for cheese in cheeses if not is_visited_cheese[cheese]), key=lambda cheese: self.simplified_graph[greedy_permutation[-1]][cheese]["distance"])
            greedy_permutation.append(best_cheese)
            is_visited_cheese[best_cheese] = True
        
        return greedy_permutation