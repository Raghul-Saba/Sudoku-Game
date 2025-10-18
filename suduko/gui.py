import tkinter as tk
from tkinter import messagebox
import time
from suduko.generator import generate_sudoku, is_valid


class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Game")
        self.geometry("500x600")
        self.resizable(False, False)
        self.start_time = None
        self.timer_label = None
        self.grid_entries = []
        self.original_puzzle = None
        self._create_start_screen()

    def _create_start_screen(self):
        """Initial start screen"""
        self.start_frame = tk.Frame(self)
        self.start_frame.pack(expand=True)
        tk.Label(self.start_frame, text="Welcome to Sudoku!", font=("Arial", 20)).pack(pady=20)
        tk.Button(self.start_frame, text="Start Game", command=self._start_game, font=("Arial", 14), 
                 bg="lightblue", padx=20, pady=10).pack(pady=10)

    def _start_game(self):
        """Switch to game view"""
        self.start_frame.destroy()
        self._create_game_screen()

    def _create_game_screen(self):
        """Game screen with grid and timer"""
        # Timer setup
        self.timer_label = tk.Label(self, text="Time: 00:00", font=("Arial", 14), fg="blue")
        self.timer_label.pack(pady=5)
        self.start_time = time.time()
        self._update_timer()

        # Sudoku grid with colored visual separation
        self.grid_frame = tk.Frame(self, bg="black")  # Black background for grid lines
        self.grid_frame.pack(pady=10)
        
        puzzle = generate_sudoku()
        self.original_puzzle = [row[:] for row in puzzle]  # Keep a copy of original

        self.grid_entries = []
        for i in range(9):
            row_entries = []
            for j in range(9):
                value = puzzle[i][j]
                
                # Create frame for each cell with colored borders
                cell_frame = tk.Frame(self.grid_frame, bg="green", relief="flat", bd=1)
                cell_frame.grid(row=i, column=j, padx=0, pady=0, sticky="nsew")
                
                # Add thicker green borders for 3x3 box separation
                if i % 3 == 0 and i > 0:  # Top border of 3x3 box
                    cell_frame.config(bd=3, bg="darkgreen")
                elif i % 3 == 2:  # Bottom border of 3x3 box  
                    cell_frame.config(bd=3, bg="darkgreen")
                elif j % 3 == 0 and j > 0:  # Left border of 3x3 box
                    cell_frame.config(bd=3, bg="darkgreen")
                elif j % 3 == 2:  # Right border of 3x3 box
                    cell_frame.config(bd=3, bg="darkgreen")
                
                # Create entry widget inside the cell frame
                entry = tk.Entry(cell_frame, width=2, font=("Arial", 18), justify="center", 
                               relief="flat", bd=0, bg="white")
                entry.pack(fill="both", expand=True, padx=1, pady=1)
                
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state="disabled", disabledforeground="black", bg="lightgray")
                else:
                    # Bind validation for empty cells
                    entry.bind('<KeyRelease>', lambda e, row=i, col=j: self._validate_input(e, row, col))
                    entry.bind('<FocusOut>', lambda e, row=i, col=j: self._validate_input(e, row, col))
                
                row_entries.append(entry)
            self.grid_entries.append(row_entries)
        
        # Configure grid weights for better spacing
        for i in range(9):
            self.grid_frame.grid_rowconfigure(i, weight=1)
        for j in range(9):
            self.grid_frame.grid_columnconfigure(j, weight=1)

        # Control buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="New Game", command=self._reset_game, 
                 bg="lightgreen", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Check Solution", command=self._check_solution, 
                 bg="orange", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Solve", command=self._solve_puzzle, 
                 bg="yellow", padx=10).pack(side=tk.LEFT, padx=5)

    def _validate_input(self, event, row, col):
        """Validate user input"""
        entry = self.grid_entries[row][col]
        value = entry.get()
        
        if value == "":
            return
        
        try:
            num = int(value)
            if num < 1 or num > 9:
                entry.delete(0, tk.END)
                return
            
            # Check if move is valid
            if not is_valid(self._get_current_board(), row, col, num):
                entry.config(bg="lightcoral")
            else:
                entry.config(bg="white")
                
        except ValueError:
            entry.delete(0, tk.END)

    def _get_current_board(self):
        """Get current state of the board"""
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                value = self.grid_entries[i][j].get()
                if value == "":
                    row.append(0)
                else:
                    try:
                        row.append(int(value))
                    except ValueError:
                        row.append(0)
            board.append(row)
        return board

    def _check_solution(self):
        """Check if current solution is correct"""
        board = self._get_current_board()
        
        # Check if board is complete
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    messagebox.showinfo("Incomplete", "Please fill in all cells!")
                    return
        
        # Check if solution is valid
        for i in range(9):
            for j in range(9):
                if not is_valid(board, i, j, board[i][j]):
                    messagebox.showinfo("Incorrect", "The solution is not correct!")
                    return
        
        messagebox.showinfo("Congratulations!", "You solved the Sudoku correctly!")
        self._reset_game()

    def _solve_puzzle(self):
        """Auto-solve the puzzle"""
        from suduko.generator import solve_sudoku
        board = self._get_current_board()
        
        if solve_sudoku(board):
            for i in range(9):
                for j in range(9):
                    if self.original_puzzle[i][j] == 0:  # Only fill originally empty cells
                        self.grid_entries[i][j].delete(0, tk.END)
                        self.grid_entries[i][j].insert(0, str(board[i][j]))
                        self.grid_entries[i][j].config(bg="lightgreen")
        else:
            messagebox.showinfo("Error", "This puzzle cannot be solved!")

    def _update_timer(self):
        """Update timer every second"""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.config(text=f"Time: {mins:02}:{secs:02}")
        self.after(1000, self._update_timer)

    def _reset_game(self):
        """Reset grid with new Sudoku"""
        for widget in self.winfo_children():
            widget.destroy()
        self._create_game_screen()
