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

<In this file, 3 players have been created (Exhaustive have been had just to be compared with Greedy):
- Exhaustive
- Greedy
- GreedyEachCheese
- GreedyEachTurn
- Cluster_man
- AI
- AI_enhancement
We were aiming at finding the shortest path to multiple cheese with the
most economical time cost.

Exhaustive: Perform a TSP to know the best order to catch the cheeses fastly

Greedy: Greedy algorithm using the heuristic : "go to the closest cheese"

GreedyEachTurn: Same as Greedy but when it searchs for the next cheese it takes in count the cheeses already taken

GreedyEachCheese: Same as GreedyEachTurn but if the cheese it was chasing is catch by the opponent it goes to the next cheese

Cluster_man: Create clusters of cheese and take it into account when searching the closest cheese. Have to be improves with a second field of larger clusters and machine learning

AI: Neural network that failed to be usefull

AI_enhancement: program to reinforce AI


>



# Games

*Please write here a few lines on the game scripts you created.*
*What are they made for?*
*Did you change some game parameters? If so, which ones and why?*

<visualize_... display a game with just the player.
match_... display a game where the two players clash.
>

# Unit tests

*Please write here a few lines on the tests you designed.*
*What are they testing?*
*Do you test some error use cases?*
*Are there some missing tests you would have liked to make?*

<We used the template file given in the session 2. We defined a maze and
solved the maze.>



# Utils

*Did you provide anything in the `utils` directory?*
*What are those files?*

<generalutils: centralizes all the main methods used
current_network: current network use by AI
412925.0_43save: save of the best network already made (in 20 hours of reinforcement)
>

# Data
<compare_exhaustive_greedy: measures time of preprocessing and turns needed to catch all cheeses for exhaustive and greedy, and compare them on the four graphs in .png.
data_matchs_... : perform many games confronting two players and display the percentage of win for each one and the average difference of the scores.

>

# Documentation

*Anything to say regarding the documentation?*





# Others

*If you had to answer particular questions in the practical session, write your answers here*
*Did you make some interesting analyses?*
*Does your code have particular dependencies we should install ?*
*Anything else to add?*

<write here>

