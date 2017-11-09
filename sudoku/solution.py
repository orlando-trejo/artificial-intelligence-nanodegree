assignments = []

# Code provided
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
# Implement naked twins strategy
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    ## Start by finding all boxes with two values
    two_vals = [box for box in boxes if len(values[box])==2]
    ## Next, find peer boxes that have matching values (twins)
    twins = [[box_i, box_j] for box_i in two_vals for box_j in peers[box_i] if values[box_i] == values[box_j]]
    # Eliminate the naked twins as possibilities for their peers
    for twin in twins:
        # Find the shared peers of each of twins
        twin_peers = list(set(peers[twin[0]]).intersection(set(peers[twin[1]])))
        for peer in twin_peers:
            if values[peer] != values[twin[0]]:
                for value in values[twin[0]]:
                    # Remove the twin values from peers
                    values[peer] = values[peer].replace(value, '')
    return values


# Code from Udacity Sudoku Lesson
def cross(A, B):
    "Cross product of elements in A and elements in B."
    # Return string combinations from each A element with each B element
    return [s+t for s in A for t in B]

# Code from Udacity Sudoku Lesson
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
    # Initialize characters
    chars = []
    # Define digits of interest
    digits = '123456789'

    for c in grid:
        # Append characters w/ found digits
        if c in digits:
            chars.append(c)
        # Replace periods with list of digits
        if c == '.':
            chars.append(digits)

    # Verify length of characters
    assert len(chars) == 81
    # Conver to dictionary
    return dict(zip(boxes, chars))

# Code from Udacity Sudoku Lesson
def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Define width of Sudoku display
    width = 1+max(len(values[s]) for s in boxes)
    # Define line to add for display separations
    line = '+'.join(['-'*(width*3)]*3)
    # Fill in rows of display
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

# Code from Udacity Sudoku Lesson
def eliminate(values):
    # Identify boxes of length 1 to identify solved boxes
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
    # Go through each solved box
    for box in solved_boxes:
        # Find the value of solved box
        value = values[box]
        # Eliminate value of solved box from peers
        for peer in peers[box]:
            values[peer] = values[peer].replace(value, '')
    # Return updated values
    return values

# Code from Udacity Sudoku Lesson
def only_choice(values):
    # Go through each unit and check
    for unit in unitlist:
        # Go through each digit
        for digit in '123456789':
            # Find boxes with digit
            dplaces = [box for box in unit if digit in values[box]]
            # Find boxes of length 1
            if len(dplaces) == 1:
                # Assign only choic value to box
                values[dplaces[0]] = digit
    return values

# Code from Udacity Sudoku Lesson
def reduce_puzzle(values):
    # Intialize criteria for ending while loop
    stalled = False
    while not stalled:
        # Initialize criteria for stalling
        solved_boxes_initial = len([box for box in values.keys() if len(values[box]) == 1])
        # Run elimination algorithm on values
        values = eliminate(values)
        # Run only_choice algorithm on values
        values = only_choice(values)
        # Run naked_twins algorithm on values
        values = naked_twins(values)
        # Finalize critieria for stalling
        solved_boxes_final = len([box for box in values.keys() if len(values[box]) == 1])
        # Check if stalled needs to be changed to True
        stalled = solved_boxes_initial == solved_boxes_final
        # Identify any errors while solving
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    # Return updated values
    return values

# Code from Udacity Sudoku Lesson
def search(values):
    # Run reduce_puzzle function on values
    values = reduce_puzzle(values)
    # Check for any errors in values
    if values is False:
        return False
    # Check if puzzle is solved
    if all(len(values[box]) == 1 for box in values.keys()):
        return values
    # Find unsolved boxes with minimum number of values
    n, s = min((len(values[box]), box) for box in values.keys() if len(values[box]) > 1)
    # Do recursion to investigate possible solutions
    for value in values[s]:
        # Create copy for recrusion
        new_sudoku = values.copy()
        # Define value to check during recursion
        new_sudoku[s] = value
        # Try solving puzzle
        attempt = search(new_sudoku)
        # Check if it works before continuing
        if attempt:
            return attempt




def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    # Transform grid into values
    values = grid_values(grid)
    # Search for solution of values
    values = search(values)
    # Return result of search
    return values

# Define row labels
rows = 'ABCDEFGHI'
# Define column labels
cols = '123456789'

# Create boxes using labels
boxes = cross(rows, cols)

# Define row units
row_units = [cross(r, cols) for r in rows]
# Define column units
column_units = [cross(rows, c) for c in cols]
# Define square units
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
# Define diagonal units
diagonal_units = [[rows[i]+cols[i] for i in range(len(rows))], ## Diagonal 1
                    [rows[i]+cols[::-1][i] for i in range(len(rows))]] ## Diagonal 2
# Create list of all units
unitlist = row_units + column_units + square_units + diagonal_units
# Create ditiona of units
units = dict((box, [u for u in unitlist if box in u]) for box in boxes)
# Create dictionary of peers
peers = dict((box, set(sum(units[box],[])) - set([box])) for box in boxes)

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
