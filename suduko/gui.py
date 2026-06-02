import tkinter as tk
from tkinter import messagebox
import time
from suduko.generator import generate_sudoku, is_valid


class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Game")
        self.geometry("620x760")
        self.resizable(False, False)
        self.start_time = None
        self.timer_label = None
        self.grid_entries = []
        self.board_canvas = None
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
        self.configure(bg="#f3f7ff")

        header = tk.Frame(self, bg="#f3f7ff")
        header.pack(fill="x", pady=(16, 6))

        self.timer_label = tk.Label(
            header,
            text="Time: 00:00",
            font=("Arial", 14, "bold"),
            fg="#1f4fa3",
            bg="#f3f7ff",
        )
        self.timer_label.pack()
        self.start_time = time.time()
        self._update_timer()

        board_wrapper = tk.Frame(self, bg="#f3f7ff")
        board_wrapper.pack(pady=12)

        puzzle = generate_sudoku()
        self.original_puzzle = [row[:] for row in puzzle]

        self.grid_entries = []
        self.board_canvas = tk.Canvas(
            board_wrapper,
            width=540,
            height=540,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        self.board_canvas.pack()

        self._draw_board_grid()

        cell_size = 60
        for i in range(9):
            row_entries = []
            for j in range(9):
                value = puzzle[i][j]

                entry = tk.Entry(
                    self.board_canvas,
                    width=2,
                    font=("Arial", 22),
                    justify="center",
                    relief="flat",
                    bd=0,
                    bg="white",
                    fg="#163d8f",
                    insertbackground="#163d8f",
                )
                x = j * cell_size + cell_size // 2
                y = i * cell_size + cell_size // 2
                self.board_canvas.create_window(x, y, window=entry, width=38, height=38)
                
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state="disabled", disabledforeground="#000000", bg="#eef3ff")
                else:
                    entry.bind('<KeyRelease>', lambda e, row=i, col=j: self._validate_input(e, row, col))
                    entry.bind('<FocusOut>', lambda e, row=i, col=j: self._validate_input(e, row, col))
                
                row_entries.append(entry)
            self.grid_entries.append(row_entries)

        button_frame = tk.Frame(self, bg="#f3f7ff")
        button_frame.pack(pady=14)
        
        button_style = {"font": ("Arial", 11, "bold"), "padx": 12, "pady": 6, "bd": 0}
        tk.Button(button_frame, text="New Game", command=self._reset_game, bg="#d7edff", fg="#123b7a", **button_style).pack(side=tk.LEFT, padx=6)
        tk.Button(button_frame, text="Check Solution", command=self._check_solution, bg="#1f4fa3", fg="white", **button_style).pack(side=tk.LEFT, padx=6)
        tk.Button(button_frame, text="Solve", command=self._solve_puzzle, bg="#d7edff", fg="#123b7a", **button_style).pack(side=tk.LEFT, padx=6)

    def _draw_board_grid(self):
        """Draw the Sudoku grid to match the board styling."""
        if self.board_canvas is None:
            return

        self.board_canvas.delete("grid")

        size = 540
        cell_size = size // 9
        thin_color = "#2f63b7"
        thick_color = "#194a9e"

        self.board_canvas.create_rectangle(0, 0, size, size, outline=thick_color, width=4, tags="grid")

        for index in range(1, 9):
            x = index * cell_size
            line_width = 4 if index % 3 == 0 else 1
            line_color = thick_color if index % 3 == 0 else thin_color
            self.board_canvas.create_line(x, 0, x, size, fill=line_color, width=line_width, tags="grid")
            self.board_canvas.create_line(0, x, size, x, fill=line_color, width=line_width, tags="grid")

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
