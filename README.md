# Checkers_AI
This is a checker's AI solver that returns the optimal moves for both players using a depth-first minimax alpha-beta pruning algorithm and custom heuristics.

The algorithm performs a minimax search with a specified depth limit and alpha-beta pruning. The program takes in a puzzle in which red is guaranteed to win and will return the optimal moves for each player showing how the game would play out provided both red and black play optimally. It makes use of node ordering state chaching and an evaluation function that estimates utility using a variety of domain advantages such as a number of pieces, prioritizing advanced pieces, center pieces, corner pieces, kings, and more. 

To run this program, run the following commands in terminal:
python3 checkers.py --inputfile <input file> --outputfile <output file>

