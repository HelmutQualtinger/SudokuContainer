from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# --- Sudoku Solver and Generator Logic ---
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board): return True
                        board[row][col] = 0
                return False
    return True

def generate_full_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    # Fill the board completely
    def fill_board(b):
        for row in range(9):
            for col in range(9):
                if b[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums) # Randomize numbers for different puzzles
                    for num in nums:
                        if is_valid(b, row, col, num):
                            b[row][col] = num
                            if fill_board(b): return True
                            b[row][col] = 0
                    return False
        return True
    fill_board(board)
    return board

def remove_cells(board, difficulty=40): # Adjust difficulty (number of cells to remove)
    puzzle = [row[:] for row in board] # Deep copy
    cells_to_remove = difficulty
    while cells_to_remove > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if puzzle[row][col] != 0:
            original_value = puzzle[row][col]
            puzzle[row][col] = 0

            # Check if puzzle is still uniquely solvable (simplified check)
            temp_board = [r[:] for r in puzzle]
            solutions_count = 0
            
            # Simple check, a proper check would require finding all solutions
            # For simplicity, we assume if one solution is found, it's good enough
            # A truly unique solver check is much more complex
            if solve(temp_board):
                solutions_count = 1 # Found at least one solution
            
            if solutions_count == 1:
                cells_to_remove -= 1
            else:
                puzzle[row][col] = original_value # Revert if not uniquely solvable (or if unsolvable)
    return puzzle


# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate_sudoku():
    full_board = generate_full_board()
    puzzle = remove_cells(full_board, difficulty=random.randint(40, 55)) # Random difficulty
    
    # Identify which cells are pre-filled (fixed)
    initial_puzzle_state = [row[:] for row in puzzle] # Store the state before solving/mutating
    fixed_cells = []
    for r in range(9):
        for c in range(9):
            if initial_puzzle_state[r][c] != 0:
                fixed_cells.append([r,c])

    return jsonify({'status': 'success', 'board': puzzle, 'fixed_cells': fixed_cells})

@app.route('/solve', methods=['POST'])
def solve_sudoku():
    data = request.json
    board = data['board']
    
    # Make a deep copy as solve modifies the board in-place
    board_copy = [row[:] for row in board] 
    
    if solve(board_copy):
        return jsonify({'status': 'success', 'board': board_copy})
    return jsonify({'status': 'error', 'message': 'Das Sudoku ist nicht lösbar oder hat einen Fehler.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True for easier development