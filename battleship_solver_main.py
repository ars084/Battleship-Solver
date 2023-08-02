from battleship_solver import ship, turn, board
import numpy as np
import copy

row = [2,4,3,1,1,2,4,1,2,0]
column = [0,4,1,1,2,3,2,3,2,2]

row = np.array(row)
column = np.array(column)
largest_ship = 4

newboard = board(row,column,largest_ship, verbose = False)

newboard.chance[4][7] = 1
newboard.chance[3][7] = 0
newboard.chance[5][7] = 0
newboard.chance[4][6] = 0
newboard.chance[4][8] = 0

newboard.chance[9][6] = 1
newboard.chance[8][6] = 1
newboard.chance[7][6] = 1

newboard.chance[0][2] = 0
newboard.chance[1][2] = 1
newboard.chance[2][2] = 1
newboard.chance[3][2] = 1
newboard.chance[4][2] = 0



newboard.full_update()
newboard.show_board()

newboard.solve()
