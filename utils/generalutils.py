#####################################################################################################################################################
######################################################################## INFO #######################################################################
#####################################################################################################################################################

"""
    This file contains useful elements to define different utils which 
    will be used in the players as methods. Because these methods are shared
    by the players we considered it more efficient to define these function 
    in a dedicated module.
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

def dyjkstra (graph:  Graph,
                source: Integral,
                visite_to_stop: List[Integral]
              ) ->      Tuple[Dict[Integral, float], Dict[Integral, Optional[Integral]]]:
        """
            This function performs the Dyjkstra algorithm on a graph.
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

def find_way(
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

def simplify_graph( maze: Maze,
                    cheeses: List[Integral],
                    starting_vertex: Integral
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
    simplified_graph[starting_vertex] = {}

    for vertex1 in cheeses + [starting_vertex]:
        distance, routing_table = dyjkstra(maze, vertex1, cheeses + [starting_vertex])
        for vertex2 in simplified_graph:
            if vertex2 != vertex1 and vertex2 not in simplified_graph[vertex1]:
                way_between = find_way(vertex2, routing_table)
                simplified_graph[vertex1][vertex2] = {"distance" : distance[vertex2], "way" : way_between}

                # Adapt the way to go from vertex2 to vertex1
                way_between_inverse = [way_between[-1-i] for i in range(1, len(way_between))] # reverse the way and suppress the source
                way_between_inverse.append(vertex1)

                simplified_graph[vertex2][vertex1] = {"distance" : distance[vertex2], "way" : way_between_inverse}

    return simplified_graph