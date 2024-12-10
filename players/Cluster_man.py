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

class Cluster_man (Player):

    """
        This player is basically a player that does nothing except printing the phase of the game.
        It is meant to be used as a template to create new players.
        Methods "preprocessing" and "postprocessing" are optional.
        Method "turn" is mandatory.
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
        self.CLUSTER_DISTANCE_MAX = 5
        self.score = game_state.score_per_player
        
        self.simplified_graph = self.simplify_graph(maze, game_state.cheese, game_state.player_locations[self.name])

        self.clusters, self.cluster_identification = self.clusterize(self.simplified_graph, game_state.cheese, self.CLUSTER_DISTANCE_MAX)

        already_print = []
        for cheese in game_state.cheese:
            if self.cluster_identification[cheese] not in already_print:
                print("Cluster", self.cluster_identification[cheese], ":", self.clusters[self.cluster_identification[cheese]]["list"])
                already_print.append(self.cluster_identification[cheese])

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

        if game_state.score_per_player != self.score:
            self.update_clusters(game_state, self.simplified_graph)
            self.score = game_state.score_per_player

        distance, routing_table = self.dyjkstra(maze, game_state.player_locations[self.name], game_state.cheese)
        closest_cheese = self.find_closest_cheese(game_state.cheese, distance, self.cluster_identification, self.clusters)
        way = self.find_way(closest_cheese, routing_table)

        action = maze.locations_to_action(game_state.player_locations[self.name], way[0])

        # Return an action
        return action

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

        # Print phase of the game
        ()

#####################################################################################################################################################
#####################################################################################################################################################


    def simplify_graph( self: Self,
                        maze: Maze,
                        cheeses: List[Integral],
                        starting_vertexe: Integral
                        ) -> Graph:
        """
            Create the simplify graph with only the cheeses and the source
            The "weight" of edges is a couple of the distance between the two vertices and the way between them
            In:
                * maze : The maze.
                * cheeses : The list of cheeses.
                * starting_vertexe : The starting vertexe.
            Out:
                * The simplified graph.
        """

        simplified_graph = {cheese: {} for cheese in cheeses}
        simplified_graph[starting_vertexe] = {}

        for vertex1 in cheeses + [starting_vertexe]:
            distance, routing_table = self.dyjkstra(maze, vertex1, cheeses + [starting_vertexe])
            for vertex2 in simplified_graph:
                if vertex2 != vertex1 and vertex2 not in simplified_graph[vertex1]:
                    way_between = self.find_way(vertex2, routing_table)
                    simplified_graph[vertex1][vertex2] = {"distance" : distance[vertex2], "way" : way_between}

                    # Adapt the way to go from vertex2 to vertex1
                    way_between_inverse = [way_between[-1-i] for i in range(1, len(way_between))] # reverse the way and suppress the source
                    way_between_inverse.append(vertex1)

                    simplified_graph[vertex2][vertex1] = {"distance" : distance[vertex2], "way" : way_between_inverse}

        return simplified_graph
    
    def clusterize( self: Self,
                    simplified_graph: Graph,
                    cheeses: List[Integral],
                    distance_max: Integral = 5
                    ) -> Tuple[Dict[Integral, List[Integral]], Dict[Integral, Integral]]:
        """
            Create the clusters of the cheeses
            In:
                * simplified_graph : The simplified graph.
                * cheeses : The list of cheeses.
                * distance_max : The maximum distance between two cheeses to be in the same cluster.
            Out:
                * The clusters.
        """

        clusters = [{"list": {cheeses[i]}, "average_distance": 0} for i in range(len(cheeses))]
        cluster_identification = {cheeses[i] : i for i in range(len(cheeses))}

        for cheese1 in cheeses:
            for cheese2 in cheeses:
                if cheese2 not in clusters[cluster_identification[cheese1]]["list"]:
                    if simplified_graph[cheese1][cheese2]["distance"] < distance_max:
                        # Merge the two clusters
                        clusters[cluster_identification[cheese1]]["list"] = clusters[cluster_identification[cheese1]]["list"] | clusters[cluster_identification[cheese2]]["list"]
                        # Update the identification
                        for cheese in clusters[cluster_identification[cheese2]]["list"]:
                            cluster_identification[cheese] = cluster_identification[cheese1]

        for cluster in clusters:
            if len(cluster["list"]) > 1:
                cluster["average_distance"] = sum([simplified_graph[cheese1][cheese2]["distance"] for cheese1 in cluster["list"] for cheese2 in cluster["list"] if cheese1 != cheese2]) / (len(cluster["list"])**2 - len(cluster["list"]))

        return clusters, cluster_identification

    def update_clusters( self: Self,
                         game_state: GameState,
                         simplified_graph: Graph
                         ) -> None:
        """
        """
        for i in range(len(self.clusters)):
            cheeses_to_remove = []
            for cheese in self.clusters[i]["list"]:
                if cheese not in game_state.cheese:
                    cheeses_to_remove.append(cheese)
            for cheese in cheeses_to_remove:
                self.clusters[i]["list"].remove(cheese)
        
        # Calculate the new average distance
        for cluster in self.clusters:
            if len(cluster["list"]) > 1:
                cluster["average_distance"] = sum([simplified_graph[cheese1][cheese2]["distance"] for cheese1 in cluster["list"] for cheese2 in cluster["list"] if cheese1 != cheese2]) / (len(cluster["list"])**2 - len(cluster["list"]))

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
    
    def find_closest_cheese( self: Self,
                             cheeses: List[Integral],
                             distances: Dict[Integral, float],
                             cluster_identification: Dict[Integral, Integral],
                             clusters: List[Dict[str, Any]]
                             ) -> Integral:
        """
            This method returns the closest cheese to the player.
            In:
                * distances: The distances from the player to the cheeses.
                * cluster_identification: The identification of the clusters.
                * clusters: The clusters.
            Out:
                * The closest cheese.
        """
        closest_cheese = min(cheeses, key=lambda cheese: (1*distances[cheese] - 2*len(clusters[cluster_identification[cheese]]["list"]) + 1*clusters[cluster_identification[cheese]]["average_distance"]))
        return closest_cheese


