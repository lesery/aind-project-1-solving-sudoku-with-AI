assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [s+d for s in A for d in B]

rows = 'ABCDEFGHI'
cols = '123456789'

#All boxes from A1 to I9:
boxes = cross(rows, cols)

#Rows, columns, squares and diagonals:
row_units = [cross(r, cols) for r in rows]
col_units = [cross(rows, c) for c in cols]
square_units = [cross(f,k) for f in ('ABC', 'DEF', 'GHI') for k in ('123', '456', '789')]
diagonal_units = [[rows[i] + cols[i] for i in range(len(rows))]] + [[rows[len(rows)-i-1] + cols[i] for i in range(len(rows))]]

#All units in list and in dict forms:
unit_list = row_units + col_units + square_units + diagonal_units
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)

#Peers of a box without duplications
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    grid_update = []
    for n in grid:
    	if n == '.':
    		grid_update.append('123456789') #make 123456789 instead of dot
    	else:
    		grid_update.append(n)           #leave a digit
    values = dict(zip(boxes, grid_update))  #make sudoku as dictionary from two lists of boxes and grid
    return values

#sudoku = grid_values('2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3')


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes) #max width of the box
    line = '+'.join(['-' * (width * 3)] * 3)       #line after row C and F. Length is 9 widths + plusses ('3 times of width of '-'' then '+' then '3 times of width of '-'' then '+' then '3 times of width of '-''
    for r in rows:
    	print(''.join(values[r+c].center(width) + ('|' if c in '36' else '') for c in cols)) #print line of boxes. Paste | between 34 and 67
    	if r in 'CF': 
    		print(line)
    return


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    possible_twins = [box for box in values.keys() if len(values[box]) == 2] #all the boxes with two digits
    for box in possible_twins:
    	for peer in peers[box]: 
    		if values[peer] == values[box]: #if there is a peer of a box with the same digits
    			twin_values = [peer, box, values[box]] #make list of peer, box and digits inside them
    			for unit in units[box]: 
    				if unit in units[peer]: #find a common unit of a box and its peer 
    					for digit in twin_values[2]: #eliminate every digit of naked twins in the unit, exept those boxes, containing naked twins
    						for u in unit:
    							if u not in twin_values:
    								assign_value(values, u, values[u].replace(digit,''))
    return values



def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
    	digit = values[box]
    	for peer in peers[box]:
    		assign_value(values, peer, values[peer].replace(digit,'')) #eliminate the digit from all the peers of a box, containing just this digit
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unit_list:
    	for digit in '123456789':
    		only_one = [box for box in unit if digit in values[box]]
    		if len(only_one) == 1:  #if a digit is seen only once in a unit, assign it to a box
    			assign_value(values, only_one[0], digit)
    return values


def reduce_puzzle(values):
    '''
    apply Constraint Propagation
    the function receives as input an unsolved puzzle and applies our two constraints (eliminate and only_choice) repeatedly in an attempt to solve it
    '''
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
    	solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        #run through functions eliminate, only choice and naked twins:
    	values = eliminate(values)
    	values = only_choice(values)	
    	values = naked_twins(values)
    	solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
    	stalled = solved_values_before == solved_values_after #check if everything is already solved
    	if len([box for box in values.keys() if len(values[box]) == 0]):
    		return False
    return values


def search(values):
	"""Using depth-first search and propagation, create a search tree"""
	values = reduce_puzzle(values)
	if values is False:
		return False
	if all(len(values[s]) == 1 for s in boxes):
		return values
	n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
	for value in values[s]:
		new_sudoku = values.copy()
		new_sudoku[s] = value
		try_new = search(new_sudoku)
		if try_new:
			return try_new


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

