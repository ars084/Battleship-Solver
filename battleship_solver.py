import copy
import numpy as np

class ship:
    def __init__(self,starting_point,length,vertical):
        self.index = starting_point
        self.length = length
        self.vertical = vertical
        
class turn:
    def __init__(self, ship_placed, starting_board, ending_board, other_options):
        self.ship_placed = ship_placed
        self.starting_board = starting_board
        self.ending_board = ending_board
        self.other_options = other_options

class board:
    def __init__(self,row,column,largest_ship, verbose = True):
        self.row = row
        self.column = column
        self.size = len(row)
        self.chance = np.ones((self.size,self.size))/2
        self.update_board()
        self.largest_ship = largest_ship
        self.solved = False
        self.board_history = []
        self.turn = 1
        self.turn_history = dict()
        self.repeat_turn = False
        self.verbose = verbose
        self.new_try = False
        
        if self.verbose:
            print('Initial Board setup:')
            self.show_board()

        num_ships = np.arange(largest_ship)+1
        ship_size = copy.copy(np.flip(num_ships))
        if self.size == 8:
            num_ships[-1] = num_ships[-1] - 1

        self.ships = dict(zip(ship_size,num_ships))
        
        self.board_history.append(self.chance)
        if self.verbose:
            self.show_board()    
            self.count_ships()
        
        self.check_answer()

    def update_board(self):
        
        water = self.chance == 0
        water_row = np.sum(water, 0)
        water_col = np.sum(np.rot90(water), 0)
        
        ship_count = self.chance == 1
        ship_row = np.sum(ship_count, 0)
        ship_col = np.sum(np.rot90(ship_count), 0)
        
        available_spots = (self.chance > 0) & (self.chance < 1)

        available_spots_row = np.sum(available_spots,0)
        available_spots_col = np.sum(np.rot90(available_spots),0)
        
        available_ships_row = self.row - ship_row 
        available_ships_col = self.column - ship_col
        
        
        chance_of_ship_row = np.divide(available_ships_row, available_spots_row, where=available_spots_row!=0)
        chance_of_ship_col = np.divide(available_ships_col, available_spots_col, where=available_spots_col!=0)
    
        
        row_full = np.repeat(chance_of_ship_row,self.size).reshape((self.size,self.size))
        column_full = np.repeat(chance_of_ship_col,self.size).reshape((self.size,self.size))
        
        find_ships = (np.maximum(np.rot90(row_full), column_full) == 1) | ship_count
        self.chance = np.multiply(np.rot90(row_full), column_full)

        self.chance[find_ships] = 1
        self.chance[water] = 0
        self.chance = self.chance.round(2)
        self.update_ship_corners()
    
    def full_update(self):
        # This runs update until a ship needs to be placed
        referencecopy = copy.copy(self.chance)
        self.update_board()
        while not np.allclose(referencecopy, self.chance):
            referencecopy = copy.copy(self.chance)
            self.update_board()
        
    def update_ship_corners(self):
        ship_indices = np.transpose(np.nonzero(self.chance == 1))
        for ship_index in ship_indices:
            # Check for boundaries
            if ship_index[0]-1 >= 0 and ship_index[1]-1 >= 0:
                self.chance[ship_index[0]-1][ship_index[1]-1] = 0
                
            if ship_index[0]+1 < self.size and ship_index[1]-1 >= 0:
                self.chance[ship_index[0]+1][ship_index[1]-1] = 0
                
            if ship_index[0]-1 >= 0 and ship_index[1]+1 < self.size:
                self.chance[ship_index[0]-1][ship_index[1]+1] = 0
                
            if ship_index[0]+1 < self.size and ship_index[1]+1 < self.size:
                self.chance[ship_index[0]+1][ship_index[1]+1] = 0
    
    def guess_ship_spots(self, ship_length):
        filt = np.ones(ship_length)
        fits = []
        ok = np.concatenate([self.chance, np.rot90(self.chance)]) #create a matrix of all col and rows
        allowance = np.concatenate([self.column, np.flip(self.row)])
        if ship_length == 1: #options get double counted for ship length 1 since we look at board + rot(board) and ship length 1 has no direction
            ok = self.chance
            allowance = self.column
        
        for i, row in enumerate(ok):
            filtlist = []
            if (np.sum((row > 0)) < ship_length) or (np.sum(row == 1) + 1 > allowance[i]) or (ship_length > allowance[i]): #exclude if not enough space
                filtlist = np.zeros(len(row))
                fits.append(filtlist)
                continue

            for j, element in enumerate(row): # search over patch in row
                if j+ship_length > len(row): # exclude if not enough space
                    filtlist.append(0)
                    continue
                if 0 in row[j:j+ship_length]: # exclude if water in patch
                    filtlist.append(0)
                    continue
                if (j > 0) and row[j-1] == 1: #exclude if cell behind patch is a boat
                    filtlist.append(0)
                    continue
                if (j+ship_length < len(row)) and (row[j+ship_length]) == 1: #exclude if cell in front of a patch is a boat
                    filtlist.append(0)
                    continue
                patch = row[j:j+ship_length]
                
                theoretical_ship_total = np.sum(row == 1) + ship_length - np.sum(patch == 1)
                if theoretical_ship_total > allowance[i]:
                    filtlist.append(0)
                    continue
                if np.sum((patch < 1) & (patch > 0)) == 0:
                    filtlist.append(0)
                    continue
                filtlist.append(np.dot(patch,filt)/ship_length)
            fits.append(filtlist)
        self.fits_array = np.array([x for x in fits])   
        
    def get_list_possible_positions(self):
        best_indices = []
        vertical_placement = []
        
        nextbest = copy.copy(self.fits_array)
        while np.max(nextbest) > 0:
            best_index = np.unravel_index(np.argmax(nextbest), self.fits_array.shape)
            best_indices.append(best_index)
            
            if best_index[0] >= self.chance.shape[0]:
                vertical_placement.append(True)
            else:
                vertical_placement.append(False)
                
            nextbest[best_index[0], best_index[1]] = 0
            
        options = len(best_indices)
        if self.verbose:
            print(f'{options} possible positions found')
        
        if options == 0:
            if self.verbose:
                print(f'No spots found')
            #revert and change ship_length += 1
            return None, None
        else:
            if self.verbose:
                print(best_indices)
            return best_indices, vertical_placement

        
        
    def place_ship_auto(self, index, vertical, ship_length):
        
        self.board_history.append(self.chance)
        
        if vertical: #place ship and pad the sides
            if self.verbose:
                print(f'Placing ship of length {ship_length}, vertically at {index}')
            
            row_place = index[1]
            column_place = 2*self.size - index[0] - 1
            
            self.chance[row_place:row_place+ship_length,column_place] = 1

            if row_place+ship_length+1 < self.size:
                self.chance[row_place+ship_length,column_place] = 0
            if row_place > 0:
                self.chance[row_place -1,column_place] = 0
        else:
            if self.verbose:
                print(f'Placing ship of length {ship_length}, horizontally at {index}')
            
            self.chance[index[0],index[1]:index[1]+ship_length] = 1

            if index[1]+ship_length+1 < self.size:
                self.chance[index[0],index[1]+ship_length] = 0
            if index[1] > 0:
                self.chance[index[0],index[1]-1] = 0
        
        self.last_ship_placed = ship(index, ship_length, vertical)
        self.board_history.append(self.chance)
            
    def count_ships(self):
        if self.verbose:
            print('Counting ships...')
        ok = np.concatenate([self.chance, np.rot90(self.chance)]) #create a matrix of all col and rows
        self.remaining_ships = dict()
        
        for key in self.ships.keys():

            if key == 1:
                new = np.pad(self.chance,1,mode='constant')
                key_counter = []
                for x in range(new.shape[0]-2):
                    test = []
                    for y in range(new.shape[1]-2):
                        filt_single = np.array([[0,0,0],[0,1,0],[0,0,0]])
                        tester = np.sum(new[x:x+3,y:y+3] == filt_single) == 9
                        test.append(tester)
                    key_counter.append(test) 
                key_counter = np.array([key_line for key_line in key_counter])
                self.remaining_ships[key] = self.ships[key] - np.sum(key_counter)
                continue 

            key_counter = []
            for row in ok:
                counter = []
                for j,element in enumerate(row):
                    if j+copy.copy(key) > len(row):
                        counter.append(0)
                        continue
                    if np.sum(row[j:j+key] < 1) > 0:
                        counter.append(0)
                        continue
                    if j+copy.copy(key)+1 <= len(row):
                        if row[j+key] > 0:
                            counter.append(0)
                            continue
                    if j>0:
                        if row[j-1] > 0:
                            counter.append(0)
                            continue
                    counter.append(1)

                key_counter.append(counter)  
            key_counter = np.array([key_line for key_line in key_counter])
            self.remaining_ships[key] = self.ships[key] - np.sum(key_counter)
        if self.verbose:
            for key in self.remaining_ships.keys():
                print(f'There are {self.remaining_ships[key]} ships remaining of size {key}')
            print('')
        self.total_remaining = np.sum([self.remaining_ships[key] for key in self.remaining_ships.keys()])
    
    def check_answer(self):
        ship_count = self.chance == 1
        water_count = self.chance == 0
        diffrow = self.row - np.sum(ship_count,0)
        diffcol = self.column - np.sum(np.rot90(ship_count),0)
        self.new_try = False
        self.count_ships()

        if np.any(diffrow < 0) or np.any(diffcol<0):
            if self.verbose:
                print('need to redo this step')
            self.new_try = True
            
        if self.total_remaining == 0 or np.all(ship_count|water_count):
            if self.verbose:
                print('you have reached an endpoint')
            ship_row = np.sum(ship_count, 0)
            ship_col = np.sum(np.rot90(ship_count), 0)

            if np.array_equiv(ship_row, self.row) & np.array_equiv(ship_col, self.column):

                for key in self.remaining_ships.keys():
                    if self.remaining_ships[key] != 0:
                        if self.verbose:
                            print('but there are errors')
                            self.show_board()
                            print(' ')
                            print('reverting to earlier play')
                        self.chance = self.starting_board
                        self.new_try = True
                        return
                print('')
                print('This is a possible solution')
                print(self.chance)
                    
                self.solved = True
                return
            else:
                if self.verbose:
                    print('but there are errors')
                    self.show_board()
                    print(' ')
                    print('reverting to earlier play')
                self.chance = self.starting_board
                self.new_try = True
                return
        if self.verbose:
            print('This fits')
        
    def show_board(self):
        print(self.chance)
        print('')
        
    def convert_to_index(index, vertical, shiplength):
        if vertical: #place ship and pad the sides
            row_place = index[1]
            column_place = 2*self.size - index[0] - 1
            
            self.chance[row_place:row_place+ship_length,column_place] = 1
            
            indices = [[row_place+i, column_place] for i in range(ship_length)]
            
        else:
            row_place = index[0]
            column_place = index[1]
            
            indices = [[row_place, column_place+i] for i in range(ship_length)]
            
        return indices

    def main_turn(self):
        
        if self.solved:
            return

        if self.verbose:
            print('')
            print(f'Turn: {self.turn}')
            print(f'Repeated turn: {self.repeat_turn}')
            print('')
            print(f'Starting board:')
            self.show_board()
        
        if self.turn == 1:
            self.full_update()
        
        if self.repeat_turn == False: # for any turn
            # Then we see what ship we need next
            self.starting_board = copy.copy(self.chance)
            self.count_ships()
            remaining = [self.remaining_ships[key] for key in self.remaining_ships.keys()]

            if np.sum(np.array(remaining) < 0) > 0: #There's been an illegal placement
                best_indices, vertical_placement = [], []
                
            elif self.total_remaining > 0: # If there's boats to place
                largest_available_ship = next(x[0] for x in enumerate(remaining) if x[1] > 0)
                next_ship_to_place = [key for key in self.remaining_ships][largest_available_ship]
                if self.verbose:
                    print(f'Trying to place ship of length {next_ship_to_place}')
                self.guess_ship_spots(next_ship_to_place)
                best_indices, vertical_placement = self.get_list_possible_positions()
            
            else: #none left to place, let's check if it's right
                if self.verbose:
                    print('Board is full, checking answer')
                self.check_answer()
                if self.solved:
                    print(self.chance)
                    return
 
        else: #for a repeated turn, we already have all of that
            self.count_ships()
            remaining = [self.remaining_ships[key] for key in self.remaining_ships.keys()]
            largest_available_ship = next(x[0] for x in enumerate(remaining) if x[1] > 0)
            next_ship_to_place = [key for key in self.remaining_ships][largest_available_ship]
            
            best_indices, vertical_placement = self.old_options
            if self.verbose:
                print(f'Trying to place ship of length {next_ship_to_place}')
                print(best_indices)
            
            
            
            self.repeat_turn = False
        
        
        if best_indices:
            
            #Then we place it
            self.place_ship_auto(best_indices[0], vertical_placement[0], next_ship_to_place)
            best_indices.pop(0)
            vertical_placement.pop(0)

            #Then we update the board
            self.full_update()

            #Save our guess
            self.check_answer()

            #check to see if you're done
            while self.new_try and best_indices:
                #Then we place it again
                self.starting_board = copy.copy(self.chance)
                if self.verbose:
                    print('Before placing:')
                    print(self.chance)
                    print(best_indices)
                
                self.place_ship_auto(best_indices[0], vertical_placement[0], next_ship_to_place)
                    
                if self.verbose:
                    print('After placing:')
                    print(self.chance)
                
                best_indices.pop(0)
                vertical_placement.pop(0)
                self.full_update()
                
                if self.verbose:
                    print('After updating:')
                    print(self.chance)
                
                #check again
                self.check_answer()
                
                if self.new_try:
                    self.chance = self.starting_board
                
        
        if not best_indices and self.new_try:
            #go back a turn
            if self.verbose:
                print(f'No place for ship of length {next_ship_to_place}')
            self.turn = self.turn-1
            
            if self.verbose:
                print(f'Returning to turn {self.turn} to replace ship of length {self.turn_history[self.turn].ship_placed.length}')
            
            self.repeat_turn = True
            
            if self.turn >= 1 and (next_ship_to_place != self.largest_ship):
                self.chance = self.turn_history[self.turn].starting_board
                self.old_options = self.turn_history[self.turn].other_options
                self.last_ship_placed = self.turn_history[self.turn].ship_placed
                self.main_turn()
                return
                
            else:
                print('Puzzle is impossible :(')
                
        other_options = [best_indices, vertical_placement]
        
        ending_board = self.chance
        
        self.turn_history[self.turn] = turn(self.last_ship_placed, self.starting_board, ending_board, other_options)
        
        self.turn += 1
        if self.verbose:
            print(f'Onto turn {self.turn}')
        
    
    def solve(self):
        while self.solved == False:
            self.main_turn()
        return self.chance

    