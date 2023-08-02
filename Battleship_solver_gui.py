import tkinter as tk

import numpy as np

import copy

from battleship_solver import ship, turn, board

class popupWindow(object):
    def __init__(self,master):
        top=self.top=tk.Toplevel(master)
        self.l=tk.Label(top,text='Enter the top row values (1, 0, 3, ...)')
        self.l.pack()
        
        self.input_row = tk.Entry(top)
        self.input_row.pack()

        self.l2=tk.Label(top,text='Enter the left column values')
        self.l2.pack()

        self.input_column = tk.Entry(top)
        self.input_column.pack()
        
        self.b=tk.Button(top,text='Ok',command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        root.input_row = self.input_row.get().split(',')
        root.input_column = self.input_column.get().split(',')
        root.value = int(len(root.input_row))+1
        make_checkerboard(canvas)
        self.top.destroy()

def make_checkerboard(canvas):
	# draw the vertical lines
	
	line_distance = int((canvas_height)/int(root.value))
	for x in range(line_distance, canvas_width, line_distance):
		canvas.create_line(x, 0, x, canvas_height)
	for y in range(line_distance, canvas_height, line_distance):
		canvas.create_line(0, y, canvas_width, y)

	#draw bounding box
	#cavas.create_line(3,3,canvas_width,3)
	canvas.create_line(canvas_width,0,canvas_width,canvas_height)
	canvas.create_line(canvas_width,canvas_height,0,canvas_height)
	#cavas.create_line(3,canvas_height,3,3)

	refx = np.arange(line_distance, canvas_width, line_distance)
	refx = np.append(refx,canvas_width)
	refx = np.insert(refx, 0, 0)

	old_ref = 0
	root.input_row.insert(0,' ')
	root.input_column.insert(0,' ')
	for i, ref in enumerate(refx[1:]):
		if i+1 > len(root.input_row):
			break

		midx = (ref+old_ref)/2
		canvas.create_text(midx, line_distance/2, text =root.input_row[i], font=('Helvetica','30','bold'))
		canvas.create_text(line_distance/2, midx, text =root.input_column[i], font=('Helvetica','30','bold'))
		old_ref = ref
	#column = tk.Label(canvas_for_input_vertical, text = str(root.column))
	#column.pack()



def select_spot(event):
	x, y = event.x, event.y

	line_distance = int(canvas_height/int(root.value))
	refx = np.arange(line_distance, canvas_width, line_distance)
	refx = np.append(refx,canvas_width)
	refx = np.insert(refx, 0, 0)

	leftbound = np.where(refx>x)[0][0]
	rightbound = np.where(refx<x)[0][-1]

	upperbound = np.where(refx>y)[0][0]
	lowerbound = np.where(refx<y)[0][-1]
	coordinates = [refx[leftbound], refx[upperbound], refx[rightbound], refx[lowerbound]]
	square_index = [rightbound-1, lowerbound-1]
	if -1 in square_index:
		return
	if square_index not in root.black_squares and square_index not in root.x_squares and square_index not in root.blank_squares:
		canvas.create_rectangle(refx[rightbound], refx[lowerbound], refx[leftbound], refx[upperbound], fill = 'black')
		
		root.black_squares.append(square_index)
		return
	
	if square_index in root.black_squares:
		canvas.create_rectangle(refx[rightbound], refx[lowerbound], refx[leftbound], refx[upperbound], fill = 'white')
		canvas.create_text((refx[rightbound]+refx[leftbound])/2, (refx[lowerbound]+refx[upperbound])/2,text = 'X', fill='black')
		
		index = root.black_squares.index(square_index)
		root.black_squares.pop(index)
		
		root.x_squares.append(square_index)
		return

	if square_index in root.x_squares:
		canvas.create_rectangle(refx[rightbound], refx[lowerbound], refx[leftbound], refx[upperbound], fill = 'white')
		
		index = root.x_squares.index(square_index)
		root.x_squares.pop(index)

		root.blank_squares.append(square_index)
		return

	if square_index in root.blank_squares:
		canvas.create_rectangle(refx[rightbound], refx[lowerbound], refx[leftbound], refx[upperbound], fill = 'black')
		
		index = root.blank_squares.index(square_index)
		root.blank_squares.pop(index)

		root.black_squares.append(square_index)
		return


def update():
	row = np.array([int(z) for z in root.input_row[1:]])
	print('Row:')
	print(row)
	print('')
	column = np.array([int(z) for z in root.input_column[1:]])
	print('Column:')
	print(column)
	print('')
	if len(row) == 6:
		largest_ship = 3
	elif len(row) == 8:
		largest_ship = 4
	elif len(row) == 10:
		largest_ship = 4
	elif len(row) == 15:
		largest_ship = 5
	elif len(row) == 20:
		largest_ship = 7
	else:
		largest_ship = 8	
	print(f'Largest_ship = {largest_ship}')

	root.board = board(row,column,largest_ship, verbose = True)
	for x_square in root.x_squares:
		root.board.chance[x_square[1]][x_square[0]] = 0
	for black_square in root.black_squares:
		root.board.chance[black_square[1]][black_square[0]] = 1

	root.board.full_update()
	root.board.show_board()
	root.solution = root.board.chance
	root.updated = True
	show_solution()

def solve():
	if not root.updated:
		update()
	root.solution = root.board.solve()
	show_solution()

def show_solution():
	line_distance = int(canvas_height/int(root.value))
	refx = np.arange(line_distance, canvas_width, line_distance)
	refx = np.append(refx,canvas_width)
	refx = np.insert(refx, 0, 0)

	for i, row in enumerate(root.solution):
		for j, element in enumerate(row):
			if element == 0:
				canvas.create_rectangle(refx[j+1], refx[i+1], refx[j+2], refx[i+2], fill = 'white')
				canvas.create_text((refx[j+2]+refx[j+1])/2, (refx[i+1]+refx[i+2])/2,text = 'X', fill='black')
			if element == 1:
				canvas.create_rectangle(refx[j+1], refx[i+1], refx[j+2], refx[i+2], fill = 'black')

def new():
	canvas.delete("all")
	w = popupWindow(root)
	root.black_squares = []
	root.x_squares = []
	root.blank_squares = []

def reset():
	canvas.delete("all")
	root.input_row = root.input_row[1:]
	root.input_column = root.input_column[1:]
	root.black_squares = []
	root.x_squares = []
	root.blank_squares = []
	make_checkerboard(canvas)


root = tk.Tk()
root.title('Test for drawing')

w = popupWindow(root)

canvas_width = 300
canvas_height = 300

root.black_squares = []
root.x_squares = []
root.blank_squares = []

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack(padx = 20, pady = 20)

update_button = tk.Button(root, text='Update Puzzle', command=update)
button = tk.Button(root, text='Solve Puzzle', command=solve)
update_button.pack(pady = 5, padx = 5, side = 'left')
button.pack(pady = 5, padx = 5, side = 'left')

new_button = tk.Button(root, text='New Puzzle', command=new)
reset_button = tk.Button(root, text='Reset Board', command=reset)
reset_button.pack(pady = 5, padx = 5, side = 'left')
new_button.pack(pady = 5, padx = 5, side = 'left')

root.bind('<ButtonRelease-1>', select_spot)

root.mainloop()