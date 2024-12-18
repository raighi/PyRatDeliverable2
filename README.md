# PyRatDeliverable2
"# PyRat-Project" 
# Students

- Responsible of the codes: Gaspard Durnez
- Responsible of the documentation: Nioré Corentin 
- Responsible of the unit tests: Raphaël Hierso--Iglesias



# Players

*Please write here a few lines on the players you wrote.*
*Precise which choices you made, and why.*
*If you chose to create some functions, which ones and why?*
*What is the complexity of these functions?*
*Did you use defensive programming? if so, where and how?*

<In this file, 7 players have been created (Exhaustive have been had just to be compared with Greedy):
- Exhaustive
- Greedy
- GreedyEachCheese
- GreedyEachTurn
- Cluster_man
- AI
- AI_enhancement
We were aiming at finding the shortest path to multiple cheese with the
most economical time cost. We also implemented player able to react to changes in the maze, that would be able to play against other players.

Exhaustive: Perform a TSP to know the best order to catch the cheeses fastly. The complexity of the algorithm is exponential.

Greedy: Greedy algorithm using the heuristic : "go to the closest cheese". The complexity of this algorithm depends mostly of the density of the maze. For T turns it could be O(C^2)+O(C*V^2log(v)) where C represents the number of cheese and V the vertices of the maze.

GreedyEachTurn: Same as Greedy but when it searchs for the next cheese it takes in count the cheeses already taken. The complexity is polynomial, relatively of the number of cheese and of the number of turn. It depends mostly of the density of the maze.

GreedyEachCheese: Same as GreedyEachTurn but if the cheese it was chasing is catch during the turn by the opponent it goes to the next nearest cheese the next turn. The complexity is about the same that the greedy or greedy each turn.

Cluster_man: Luster_man uses another herustic : it creates clusters of cheese and takes it into account when searching the closest cheese. Have to be improved with a second field of larger clusters and machine learning, in order to take more efficient decisions.

AI: Neural network that failed to be useful. The other methods provide a way to store new entrances on the neural network (get_entrance,edge_to_entrance_index), and the forward_propagation compute the output of the neural network. The main factor of complexity is the forward propogation which is in a complexity polynomial relatively to the number of neuron.

AI_enhancement: program to reinforce AI

We implemanted some of the player with a combination of object oriented programmation, but by defining some utils it was possible to program in a modulary way and reuse efficiently previous algorithms.
>



# Games

*Please write here a few lines on the game scripts you created.*
*What are they made for?*
*Did you change some game parameters? If so, which ones and why?*

<visualize_... display a game with just the player. We visualized all the players previosuly presented.
match_... display a game where the two players clash. 
>

# Unit tests

*Please write here a few lines on the tests you designed.*
*What are they testing?*
*Do you test some error use cases?*
*Are there some missing tests you would have liked to make?*

<We used the template file given in the session 2. We defined a maze and
solved the maze. It tests mostly the key method simplify_graph by checking its input and its output.>



# Utils

*Did you provide anything in the `utils` directory?*
*What are those files?*

<generalutils: centralizes all the main methods used
current_network: current network used by AI
412925.0_43save: save of the best network already made (in 20 hours of reinforcement)
>

# Data
<compare_exhaustive_greedy: measures time of preprocessing and turns needed to catch all cheeses for exhaustive and greedy, and compare them on the four graphs in .png.
data_matchs_... : perform many games confronting two players and display the percentage of win for each one and the average difference of the scores.

>

# Documentation

*Anything to say regarding the documentation?*

We wrote documentation for the players, the utils, and the games. We tried to generate html documentation with pydoc (and it worked) but did not know how to share it in this archive.




# Others

*If you had to answer particular questions in the practical session, write your answers here*
*Did you make some interesting analyses?*
*Does your code have particular dependencies we should install ?*
*Anything else to add?*

<write here>

