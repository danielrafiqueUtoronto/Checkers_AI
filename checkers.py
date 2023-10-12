import argparse
import copy
import sys
import time

cache = {} # you can use this to implement state caching!

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board, depth = None):

        self.board = board

        self.width = 8
        self.height = 8
        self.depth = depth

    def display(self, file):
        for i in self.board:
            for j in i:
                print(j, end="")
                file.write(f'{j}')
            file.write("\n")
            print("")
        print("")

#FUNCTIONS TO GENERATE SUCESSORS
def find_all_pieces(state, curr_turn):
    #helper function to generate sucessors
    #return a list of coordinates for pieces to analyze to generate sucessors (red or black)
    pieces = list()
    
    for i in range(8):
        for j in range(8):
            if state.board[i][j] == curr_turn[0] or state.board[i][j] == curr_turn[1]:
                piece_type = state.board[i][j]
                pieces.append([i,j, piece_type])
          
    return pieces

def attacking_moves(state, pieces, curr_turn):
    """returns list of coordinates/pieces that can attack and their cooresponding end positions same format as pieces [row, col, type]

    Args:
        pieces (_type_): _description_
        curr_turn (_type_): _description_
    """
    opp_char = get_opp_char(curr_turn[0])
    attacking_pieces = list()
    
    for coords in pieces:
        # immediate jump moves 
        #looking left
        if coords[1] >=2: #not on left edge (most left point you can attack from without going past board)
            
            #ATTACK UP LEFT
            if coords[0] >=2 and coords[2] in ['r', 'R', 'B']: #not on top 3rd row (highest row you can attack from)
                if state.board[coords[0]-1][coords[1]-1] in opp_char and state.board[coords[0]-2][coords[1]-2] == ".":
                    
                    #if the end pos is the top row AND curr_turn is red red piece, change end pos to R king
                    if coords[0]-2 == 0 and coords[2] == 'r':
                        end_pos = [coords[0]-2, coords[1]-2, 'R'] #change piece to king
                    else:
                        end_pos = [coords[0]-2, coords[1]-2, coords[2]]
                    
                    attacking_pieces.append([coords,end_pos])
            
            #ATTACK BOTTOM LEFT
            if coords[0] <6 and coords[2] in ['b', 'B', 'R']: #not on bottom 3rd row and not reg red piece
                if state.board[coords[0]+1][coords[1]-1] in opp_char and state.board[coords[0]+2][coords[1]-2] == ".":
                    
                    if coords[0]+2 == 7 and coords[2] == 'b':
                        end_pos = [coords[0]+2, coords[1]-2, 'B']
                    else:
                        end_pos = [coords[0]+2, coords[1]-2, coords[2]]
                        
                    attacking_pieces.append([coords, end_pos])
        
          
        if coords[1] <6: #not on right edge (most right point you can attack from)
            
            #ATTACK UP RIGHT
            if coords[0] >= 2 and coords[2] in ['r', 'R', 'B']:
                if state.board[coords[0]-1][coords[1]+1] in opp_char and state.board[coords[0]-2][coords[1]+2] == ".":
                    
                    if coords[0]-2 == 0 and coords[2] == 'r':
                        end_pos = [coords[0]-2, coords[1]+2, 'R']
                    else:
                        end_pos = [coords[0]-2, coords[1]+2, coords[2]]
                        
                    attacking_pieces.append([coords, end_pos])
            
            #ATTACK BOTTOM RIGHT
            if coords[0] <6 and coords[2] in ['b', 'B', 'R']:
            
                if state.board[coords[0]+1][coords[1]+1] in opp_char and state.board[coords[0]+2][coords[1]+2] == ".":
                    
                    if coords[0]+2 == 7 and coords[2] == 'b':
                        end_pos = [coords[0]+2, coords[1]+2, 'B']
                    else:
                        end_pos = [coords[0]+2, coords[1]+2, coords[2]]
                    
                    attacking_pieces.append([coords, end_pos])
        
    return attacking_pieces

def make_attack_move(new_state, piece):
    """applies the "move" or state change to attacking piece 

    Args:
        new state (State): includes the copied board we are analyzing the move for
        piece (list): includes attacking piece of type [[row,col, type], [row, col, type]] where index 0 is piece to move and index 1 is end pos
        curr_turn (list): list as [r, R] or [b, B] if its black or reds turn
    Returns:
        _type_: nothing, converts state to new state by moving the given piece
    """
    
    #make curr position into space
    new_state.board[piece[0][0]][piece[0][1]] = "."
    #set new position to new pos player char
    new_state.board[piece[1][0]][piece[1][1]] = piece[1][2]
    
    #remove opp piece we jumped over
    #if end pos col < curr pos col and end pos row is higher (<) than curr pos thne remove top left of curr
    #remove top left opp piece
    if piece[1][1] < piece[0][1] and piece[1][0] < piece[0][0]:
        new_state.board[piece[0][0]-1][piece[0][1]-1] = "."
    #remove top right opp piece
    elif piece[1][1] > piece[0][1] and piece[1][0] < piece[0][0]:
        new_state.board[piece[0][0]-1][piece[0][1]+1] = "."
    #remove bottom left opp piece
    elif piece[1][1] < piece[0][1] and piece[1][0] > piece[0][0]:
        new_state.board[piece[0][0]+1][piece[0][1]-1] = "."
    #remove bottom right
    elif piece[1][1] > piece[0][1] and piece[1][0] > piece[0][0]:
        new_state.board[piece[0][0]+1][piece[0][1]+1] = "."
        
def multi_jump_attack(new_state, piece, curr_turn):
    """returns attacking moves from end position after a jump

    Args:
        new_board (_type_): _description_
        piece (_type_): includes the end position of the piece that just jumped so looking for piece[1]
    """
    piece_list = list()
    #king check
    if piece[0][2] in ['r', 'b'] and piece[1][2] in ['R', 'B']:
        #terminate multi jump and return an empty piece list
        return piece_list
    
    piece_list.append(piece[1])
    #print(piece_list)
    multi_jumps = attacking_moves(new_state, piece_list, curr_turn)
    
    
    return multi_jumps
 
def simple_successors(state, pieces):
    #this function returns basic non attacking moves and will only be used if attacking move list is empty 
    
    #pieces = find_all_pieces(state, curr_turn) #list of POTENTIALLY movable pieces for a given colour
    simple_succ_list= list() #list of simple moves available, only to be used IF regular list is empty
    
    for coords in pieces:
        
        #simple left moves      
        if coords[1] != 0: #not on left edge
            
            if coords[0] != 0: #not on top row
                if state.board[coords[0]-1][coords[1]-1] == "." and coords[2] in ['r', 'R', 'B']:
                    new_board = copy.deepcopy(state.board)
                    if coords[0]-1 == 0 and coords[2] == 'r':
                        new_board[coords[0]-1][coords[1]-1] = 'R'
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
                    else:
                        new_board[coords[0]-1][coords[1]-1] = coords[2]
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)

            if coords[0] !=7: #not on bottom row
                if state.board[coords[0]+1][coords[1]-1] == "." and coords[2] in ['b', 'B', 'R']:
                    new_board = copy.deepcopy(state.board)
                    if coords[0]+1 == 7 and coords[2] == 'b':
                        new_board[coords[0]+1][coords[1]-1] = 'B'
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
                    else:
                        new_board[coords[0]+1][coords[1]-1] = coords[2]
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
        
        #simple right moves      
        if coords[1] != 7: #not on right edge
            
            if coords[0] != 0: #not on top row
                if state.board[coords[0]-1][coords[1]+1] == "." and coords[2] in ['r', 'R', 'B']:
                    new_board = copy.deepcopy(state.board)
                    if coords[0]-1 == 0 and coords[2] == 'r':
                        new_board[coords[0]-1][coords[1]+1] = 'R'
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
                    else:
                        new_board[coords[0]-1][coords[1]+1] = coords[2]
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)

            if coords[0] !=7: #not on bottom row
                if state.board[coords[0]+1][coords[1]+1] == "." and coords[2] in ['b', 'B', 'R']:
                    new_board = copy.deepcopy(state.board)
                    if coords[0]+1 == 7 and coords[2] == 'b':
                        new_board[coords[0]+1][coords[1]+1] = 'B'
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
                    else:
                        new_board[coords[0]+1][coords[1]+1] = coords[2]
                        new_board[coords[0]][coords[1]] = "."
                        succ_state = State(new_board)
                        simple_succ_list.append(succ_state)
                            
    return simple_succ_list 
 
def generate_successors(state, curr_turn, subsequent_attacks=None):
    successors = list()
    all_movable_pieces = find_all_pieces(state, curr_turn) #returns list of simple and attacking pieces list of [row,col, type]
    if subsequent_attacks:
        attack_moves = subsequent_attacks
        
    else:   
        attack_moves = attacking_moves(state, all_movable_pieces, curr_turn) #type attack piece [curr pos, end pos] 
    
    for piece in attack_moves:
        new_state = copy.deepcopy(state)
        make_attack_move(new_state, piece)
        subsequent_attacks = multi_jump_attack(new_state, piece, curr_turn)
        
        if subsequent_attacks:
            recursive_successors = generate_successors(new_state, curr_turn, subsequent_attacks)
            successors.extend(recursive_successors)
        else:
            successors.append(new_state)
    
    simple_moves = simple_successors(state, all_movable_pieces)
    #if there are no attacking moves return whatever simple moves are available
    if not successors:
        return simple_moves
    else:  
        return successors
   
def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

#FUNCTIONS TO ASSESS SUCESSORS FOR ALPHA-BETA PRUNING
def utility_function(state, curr_turn):
    """computes the utility of a terminal state either -1000000000 or +1000000000

    Args:
        state (State_): takes in a state to check if its a terminal state
        curr_turn (list): either ['r','R'] or ['b', 'B'] indicating which players turn it is
    """
    #winning temrinal state if I have captured all of opps pieces or opp doesn't have any legal moves
    #check # opp pieces is 0
    opp_player = get_opp_char(curr_turn[0])
    piece_list = find_all_pieces(state, opp_player)
    movable_pieces = generate_successors(state, opp_player)
    
    utility = 0
    if len(piece_list) == 0 or len(movable_pieces) == 0 and curr_turn == ['r', 'R']: #opp has no more pieces OR they have no more legal moves (blocked off)
        utility = 1000000000
    
    elif len(piece_list) == 0 or len(movable_pieces) == 0 and curr_turn == ['b', 'B']: #opp has no more pieces OR they have no more legal moves (blocked off)
        utility = -1000000000
    
    return utility

def evaluation_function(state, curr_turn, curr_depth):
    """
    takes in a state and returns an estimated evaluation of a utility value based on board attributes

    Args:
        state (_type_): board state
        curr_turn (_type_): player either red or black in 1d array 
    """
    eval = 0
    #reg piece = 1pt, Bonus points: king piece = +1 pts, center piece = +0.5 pts (row/col 2-5), edge piece = +0.15 pts, advanced piece = +0.25 
    #piece[0] is row, piecep[1] is col, piece[2] is piece type
    util = utility_function(state, curr_turn)
    if util == 1000000000 or util == -1000000000:
        return util*curr_depth
    
    piece_list = find_all_pieces(state, curr_turn)
    attacking_pieces = attacking_moves(state, piece_list, curr_turn)
    
    for i in piece_list:
        
        if i[2] in ['r', 'R']:
            eval +=1 #regular point for any piece thats red
        elif i[2] in ['b', 'B']:
            eval-=1 #regualr point for any black piece
        
        #BONUS POINTS BASED ON POSITION
        
        # +1 pt if its a king
        if i[2] == 'R':
            eval+=1
        elif i[2] == 'B':
            eval-=1
        
        #if its a center piece 
        if (i[0] >=2 and i[0] <=5) and (i[1] >=2 and i[1]<=5):
            #center reg
            if i[2] in ['r', 'R']:
                eval+=0.5
            elif i[2] in ['b', 'B']:
                eval-=0.5
        
        #if its an edge piece (can't be attacked)
        if (i[0] == 0 or i[1] == 7 or i[1] == 0 or i[1] == 7):
            
            if i[2] in ['r', 'R']:
                eval +=0.15
            elif i[2] in ['b', 'B']:
                eval-=0.15
        
        #if its advanced in the board (rows 0-3 inclusive for red or rows 4-7 inclusive for black)
        if (i[0] <= 3 and i[0] >= 0) and i[2] in ['r', 'R']:
            eval+= 0.25
        if (i[0] <= 7 and i[0] >= 4) and i[2] in ['b', 'B']:
            eval-=0.25
        
        #+0.75 points for any piece that can attack
        for i in attacking_pieces:
            if curr_turn == ['r', 'R']:
                eval+=0.75
            elif curr_turn == ['b', 'B']:
                eval-=0.75
        
    #Penalties for opp player advantages
    #-1 pt for every opp piece, Bonuses: -0.5 opp king, -0.5 opp center piece, -0.15 opp edge piece, -0.75 for opp attack pieces
    opp_turn = get_opp_char(curr_turn[0])
    piece_list_opp = find_all_pieces(state, opp_turn)
    attacking_pieces_opp = attacking_moves(state, piece_list_opp, opp_turn)
    
    for i in piece_list_opp:
    
        if i[2] in ['r', 'R']:
            eval -=1 #regular point for any piece thats red
        elif i[2] in ['b', 'B']:
            eval+=1 #regualr point for any black piece
        
        #BONUS POINTS BASED ON POSITION
        
        # +1 pt if its a king
        if i[2] == 'R':
            eval-=1
        elif i[2] == 'B':
            eval+=1
        
        #if its a center piece 
        if (i[0] >=2 and i[0] <=5) and (i[1] >=2 and i[1]<=5):
            #center reg
            if i[2] in ['r', 'R']:
                eval-=0.5
            elif i[2] in ['b', 'B']:
                eval+=0.5
        
        #if its an edge piece (can't be attacked)
        if (i[0] == 0 or i[1] == 7 or i[1] == 0 or i[1] == 7):
            
            if i[2] in ['r', 'R']:
                eval -=0.15
            elif i[2] in ['b', 'B']:
                eval+=0.15
        
        #if its advanced in the board (rows 0-3 inclusive for red or rows 4-7 inclusive for black)
        if (i[0] <= 3 and i[0] >= 0) and i[2] in ['r', 'R']:
            eval-= 0.25
        if (i[0] <= 7 and i[0] >= 4) and i[2] in ['b', 'B']:
            eval+=0.25
        
        #+0.75 points for any piece that can attack
        for i in attacking_pieces_opp:
            if opp_turn == ['r', 'R']:
                eval-=0.75
            elif opp_turn == ['b', 'B']:
                eval+=0.75
        
        
    return eval

def sort_successors(successors, curr_turn, curr_depth):
    
    ordered_dict = {}
    
    #evaluate list of successors
    for succ in successors:
        eval = evaluation_function(succ, curr_turn, curr_depth)
        ordered_dict[succ] = eval

    #sort the dictionary by value in reverse for max's children (red)
    if curr_turn[0] == 'r':
        ordered_dict = dict(sorted(ordered_dict.items(), key=lambda x:x[1], reverse=True))
        keylist =  list(ordered_dict.keys())
        return keylist
    else:
        ordered_dict = dict(sorted(ordered_dict.items(), key=lambda x:x[1]))
        keylist = list(ordered_dict.keys())
        return keylist

def alphabeta_max_node(state, curr_turn, alpha, beta, curr_depth):
    #turn state into a string and append whos turn it is before caching
    #current depth starts HIGH then goes down to ZERO
    #cached state - cashe[state][0] = state, cache[state][1] = depth, [2] = v, [3] = state sucessor
    successors = generate_successors(state, curr_turn, None)
    cache_string = str([state.board, curr_turn])
    if cache_string in cache and cache[cache_string][1] >= curr_depth:
        return (cache[cache_string][2], cache[cache_string][3])

    is_terminal = False
    if utility_function(state, curr_turn) == 1000000000:
        is_terminal = True
    
    if curr_depth == 0 or is_terminal == True:
        return (evaluation_function(state, curr_turn, curr_depth), None)
    
    if len(successors)== 0:
        #cache the states value, depth, and sucessor
        #first turn state into string to be identficable key before caching
        cache_string = str([state.board, curr_turn])
        cache[cache_string] = [state, curr_depth, -1000000000, None]
        return (-1000000000, None)
    
    #sort sucessors based on evaluation function
    sorted_succ = sort_successors(successors, curr_turn, curr_depth)
    v = float('-inf') #-infinity
    best = state
    for succ in sorted_succ:
        opp_turn = get_opp_char(curr_turn[0])
        tempval, tempstate = alphabeta_min_node(succ, opp_turn, alpha, beta, curr_depth-1)
        if tempval > v:
            v = tempval
            best = succ
        if tempval > beta:
            cache_string = str([state.board, curr_turn])
            cache[cache_string] = [state, curr_depth, v, succ]
            return (v, succ)
        alpha = max(alpha, tempval)
        cache_string = str([state.board, curr_turn])
        cache[cache_string] = [state, curr_depth, v, best]
        
    return (v, best)
    
def alphabeta_min_node(state, curr_turn, alpha, beta, curr_depth):
    
    successors = generate_successors(state, curr_turn, None)
    is_terminal = False
    if utility_function(state, curr_turn) == -1000000000:
        is_terminal = True
    
    cache_string = str([state.board, curr_turn])
    if cache_string in cache and cache[cache_string][1] >= curr_depth:
        return (cache[cache_string][2], cache[cache_string][3])
    
    if curr_depth == 0 or is_terminal == True:
        return (evaluation_function(state, curr_turn, curr_depth), state)
    
    if len(successors)== 0:
        #cache the states value, depth, and sucessor
        #first turn state into string to be identficable key before caching
        cache_string = str([state.board, curr_turn])
        cache[cache_string] = [state, curr_depth, 1000000000, None]
        return (1000000000, None)
    
    #sort sucessors based on evaluation function
    sorted_succ = sort_successors(successors, curr_turn, curr_depth)
    v = float('inf')
    best = state
    for succ in sorted_succ:
        opp_turn = get_opp_char(curr_turn[0])
        tempval, tempstate = alphabeta_max_node(succ, opp_turn, alpha, beta, curr_depth-1)
        #print(tempval)
        if tempval < v:
            v = tempval
            best = succ
        if tempval < alpha:
            cache_string = str([state.board, curr_turn])
            cache[cache_string] = [state, curr_depth, v, succ]
            return (v, succ)
        beta = min(beta, tempval)
        cache_string = str([state.board, curr_turn])
        cache[cache_string] = [state, curr_depth, v, best]
        
    return (v, best)

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    
    
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )

    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    outputfile = open(args.outputfile, "a")
    
    state = State(initial_board, 10)
    turn = 'r'
    ctr = 0
    state.display(outputfile)
    outputfile.write("\n")
    best = state
    game_done = False
    
    
    start_time = time.time()
    
    while game_done == False:
        
        v, best = alphabeta_max_node(best, ['r', 'R'], -1000000000, 1000000000, 9)
        #best.display()
        best.display(outputfile)
        outputfile.write("\n")
        ctr+=1
        if utility_function(best, ['r', 'R']) == 1000000000:
            game_done = True
            break
    
        v, best = alphabeta_min_node(best, ['b', 'B'], -1000000000, 1000000000, 9)
        #best.display()
        best.display(outputfile)
        outputfile.write("\n")
        
        ctr+=1
        if utility_function(best, ['r', 'R']) == 1000000000:
            game_done = True
            break
    
    end_time = time.time()
    
    total_time =  end_time - start_time
    #outputfile.write(f"{ctr} moves\n")
    #outputfile.write(f"{total_time} seconds")
    outputfile.close()
    print(f'{ctr} moves')
    print(f'{total_time} seconds')
    print()
    
    
    #sys.stdout = open(args.outputfile, 'w')
    #sys.stdout = sys.__stdout__

    
    