import random


def is_valid(board, row, col, num):
    """Check if placing num at (row, col) is valid"""
    # Check row
    for x in range(9):
        if board[row][x] == num:
            return False
    
    # Check column
    for x in range(9):
        if board[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    
    return True


def solve_sudoku(board):
    """Solve Sudoku using backtracking"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_sudoku():
    """Generate a valid Sudoku puzzle"""
    # Start with empty board
    board = [[0 for _ in range(9)] for _ in range(9)]
    
    # Fill diagonal 3x3 boxes first (they are independent)
    for i in range(0, 9, 3):
        fill_box(board, i, i)
    
    # Solve the rest
    solve_sudoku(board)
    
    # Remove some numbers to create puzzle
    # Remove more numbers for harder puzzle
    empty_cells = random.randint(40, 50)
    positions = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(positions)
    
    for i in range(empty_cells):
        row, col = positions[i]
        board[row][col] = 0
    
    return board


def fill_box(board, row, col):
    """Fill a 3x3 box with random numbers 1-9"""
    nums = list(range(1, 10))
    random.shuffle(nums)
    for i in range(3):
        for j in range(3):
            board[row + i][col + j] = nums[i * 3 + j]
