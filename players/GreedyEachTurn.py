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

# PyRat imports
from pyrat import Player, Maze, GameState, Action
from itertools import permutations

#####################################################################################################################################################
###################################################################### CLASSES ######################################################################
#####################################################################################################################################################

class GreedyEachTurn (Player):

    """
        Greedy player with the heuristic of the nearest cheese.
        Heuristic :
        "Le chemin le plus court qui passe par tous les morceaux de fromage peut être approximé en 
        allant séquentiellement vers le morceau de fromage le plus proche"
        This player don't calculate the path in preprocessing but as the game goes on.
        He will not run to a cheese already catch by another player.
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

        # Variables
        self.way = []
        self.closest_cheese = None
        
       
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
        self.simplified_graph = self.simplify_graph(maze, game_state)

        # Find the closest cheese
        self.closest_cheese = min( game_state.cheese, key = lambda cheese: self.simplified_graph[game_state.player_locations[self.name]][cheese]["distance"])
        self.way = self.simplified_graph[game_state.player_locations[self.name]][self.closest_cheese]["way"]


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
            self.closest_cheese = min( game_state.cheese, key = lambda cheese: self.simplified_graph[game_state.player_locations[self.name]][cheese]["distance"])
            self.way = self.simplified_graph[game_state.player_locations[self.name]][self.closest_cheese]["way"]

        if self.closest_cheese not in game_state.cheese:
            distance, routing_table = self.dyjkstra(maze, game_state.player_locations[self.name], game_state.cheese)
            self.closest_cheese = min( game_state.cheese, key = lambda cheese: distance[cheese])
            self.way = self.find_way(self.closest_cheese, routing_table)
        
        action = maze.locations_to_action(game_state.player_locations[self.name], self.way.pop(0))

        return action
    
#####################################################################################################################################################
#####################################################################################################################################################

    def dyjkstra ( self: Self,
                    graph:  Graph,
                    source: Integral,
                    visite_to_stop: List[Integral]
                  ) ->      Tuple[Dict[Integral, float], Dict[Integral, Optional[Integral]]]:
        """
            This method performs the Dyjkstra algorithm on a graph.
            In:
                * graph:  The graph on which we want to perform the Dyjkstra algorithm.
                * source: The source vertex.
                * visite_to_stop: The list of vertices to visit before stopping the algorithm.
            Out:
                * distances:     The distances from the source vertex.
                * routing_table: The routing table.
        """
        
        # Initialization
        distances = {vertex : float('inf') for vertex in graph.vertices}
        distances[source] = 0
        routing_table = {vertex : None for vertex in graph.vertices}
        is_visited = {vertex : False for vertex in graph.vertices}
        visited_to_stop = {vertex : False for vertex in visite_to_stop}
        visited_to_stop[source] = True

        # Main loop
        while not all(visited_to_stop.values()):

            # Find the closest vertex
            closest_vertex = min( (vertex for vertex in graph.vertices if not is_visited[vertex]), key=distances.get)
            is_visited[closest_vertex] = True
            visited_to_stop[closest_vertex] = True

            # Update the distances
            for neighbor in graph.get_neighbors(closest_vertex):
                if distances[neighbor] > distances[closest_vertex] + graph.get_weight(closest_vertex, neighbor):
                    distances[neighbor] = distances[closest_vertex] + graph.get_weight(closest_vertex, neighbor)
                    routing_table[neighbor] = closest_vertex
        
        return distances, routing_table


    def find_way( self: Self,
                    vertex: Integral,
                    routing_table: Dict[Integral, Optional[Integral]]
                   ) -> List[Integral]:
        """
            This method returns the way from vertex1 to vertex2 using the routing table.
            (the list contain the destination vertex but not the source vertex)
            In:
                * vertex:       The source vertex.
                * routing_table: The routing table.
            Out:
                * way: The way from vertex1 to vertex2.
        """
        way = []
        while routing_table[vertex] is not None:
            way.append(vertex)
            vertex = routing_table[vertex]     
        way.reverse()
        return way
    
    def simplify_graph( self: Self,
                        maze: Maze,
                        game_state: GameState
                        ) -> Graph:
        """
            Create the simplify graph with only the cheeses and the source
            The "weight" of edges is a couple of the distance between the two vertices and the way between them
            In:
                * maze : The maze.
                * graph: The graph to simplify.
            Out:
                * The simplified graph.
        """

        simplified_graph = {cheese: {} for cheese in game_state.cheese}
        simplified_graph[game_state.player_locations[self.name]] = {}

        for vertex1 in game_state.cheese + [game_state.player_locations[self.name]]:
            distance, routing_table = self.dyjkstra(maze, vertex1, game_state.cheese + [game_state.player_locations[self.name]])
            for vertex2 in simplified_graph:
                if vertex2 != vertex1 and vertex2 not in simplified_graph[vertex1]:
                    way_between = self.find_way(vertex2, routing_table)
                    simplified_graph[vertex1][vertex2] = {"distance" : distance[vertex2], "way" : way_between}

                    # Adapt the way to go from vertex2 to vertex1
                    way_between_inverse = [way_between[-1-i] for i in range(1, len(way_between))] # reverse the way and suppress the source
                    way_between_inverse.append(vertex1)

                    simplified_graph[vertex2][vertex1] = {"distance" : distance[vertex2], "way" : way_between_inverse}

        return simplified_graph
