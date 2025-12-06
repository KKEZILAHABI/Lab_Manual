import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import time

# Player and opponent constants
player, opponent = 'x', 'o'

class TicTacToeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe: You vs AI (with Minimax Visualization)")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Initialize game state
        self.board = [
            ['_', '_', '_'],
            ['_', '_', '_'],
            ['_', '_', '_']
        ]
        
        self.game_over = False
        self.user_turn = True  # User starts first
        self.visualization_enabled = True
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Game Board
        left_panel = tk.Frame(main_frame, relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel - AI Visualization
        right_panel = tk.Frame(main_frame, relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # === LEFT PANEL: Game Board ===
        title_label = tk.Label(left_panel, text="Tic-Tac-Toe", 
                               font=("Arial", 20, "bold"), fg="blue")
        title_label.pack(pady=10)
        
        self.status_label = tk.Label(left_panel, text="Your turn (X)", 
                                    font=("Arial", 12), fg="green")
        self.status_label.pack(pady=5)
        
        # Game board frame
        board_frame = tk.Frame(left_panel)
        board_frame.pack(pady=15)
        
        # Create buttons for the board
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    board_frame,
                    text="",
                    font=("Arial", 28, "bold"),
                    width=4,
                    height=2,
                    bg="lightgray",
                    command=lambda row=i, col=j: self.user_move(row, col)
                )
                self.buttons[i][j].grid(row=i, column=j, padx=3, pady=3)
        
        # Control buttons frame
        control_frame = tk.Frame(left_panel)
        control_frame.pack(pady=15)
        
        reset_button = tk.Button(control_frame, text="Reset Game", 
                                font=("Arial", 11), 
                                command=self.reset_game,
                                bg="lightblue", width=12)
        reset_button.grid(row=0, column=0, padx=5)
        
        exit_button = tk.Button(control_frame, text="Exit", 
                               font=("Arial", 11), 
                               command=self.root.quit,
                               bg="lightcoral", width=12)
        exit_button.grid(row=0, column=1, padx=5)
        
        # Visualization toggle
        self.viz_var = tk.BooleanVar(value=True)
        viz_check = tk.Checkbutton(left_panel, text="Show AI Visualization",
                                   variable=self.viz_var,
                                   font=("Arial", 10))
        viz_check.pack(pady=5)
        
        instructions = tk.Label(left_panel, 
                               text="You are X, AI is O\nClick a cell to make your move",
                               font=("Arial", 9), fg="gray")
        instructions.pack(pady=5)
        
        # === RIGHT PANEL: AI Visualization ===
        viz_title = tk.Label(right_panel, text="AI Decision Process", 
                            font=("Arial", 16, "bold"), fg="darkblue")
        viz_title.pack(pady=10)
        
        # Current evaluation label
        self.eval_label = tk.Label(right_panel, 
                                   text="Waiting for AI turn...",
                                   font=("Arial", 11), fg="orange")
        self.eval_label.pack(pady=5)
        
        # Scrolled text for minimax trace
        trace_frame = tk.Frame(right_panel)
        trace_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(trace_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trace_text = tk.Text(trace_frame, 
                                 font=("Courier", 9),
                                 wrap=tk.WORD,
                                 yscrollcommand=scrollbar.set,
                                 bg="#f5f5f5")
        self.trace_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.trace_text.yview)
        
        # Configure text tags for colors
        self.trace_text.tag_config("header", foreground="darkblue", font=("Courier", 9, "bold"))
        self.trace_text.tag_config("move", foreground="green", font=("Courier", 9, "bold"))
        self.trace_text.tag_config("score", foreground="red")
        self.trace_text.tag_config("best", foreground="purple", font=("Courier", 9, "bold"))
        self.trace_text.tag_config("info", foreground="blue")
        
        # Best move display
        self.best_move_label = tk.Label(right_panel,
                                       text="Best Move: --",
                                       font=("Arial", 12, "bold"),
                                       fg="purple")
        self.best_move_label.pack(pady=10)
    
    def user_move(self, row, col):
        """Handle user's move"""
        if self.game_over:
            return
            
        if not self.user_turn:
            self.status_label.config(text="Wait for your turn!", fg="orange")
            return
            
        if self.board[row][col] != '_':
            self.status_label.config(text="Cell already taken!", fg="red")
            return
            
        # Make user's move
        self.board[row][col] = player
        self.buttons[row][col].config(text="X", fg="blue", state="disabled")
        
        # Clear visualization
        self.trace_text.delete(1.0, tk.END)
        self.eval_label.config(text="Waiting for AI turn...")
        self.best_move_label.config(text="Best Move: --")
        
        # Check if game is over after user's move
        if self.check_game_over():
            return
            
        # Switch to AI's turn
        self.user_turn = False
        self.status_label.config(text="AI thinking...", fg="orange")
        
        # Schedule AI move after a short delay
        self.root.after(500, self.ai_move)
    
    def ai_move(self):
        """AI makes its move using the minimax algorithm"""
        if self.game_over:
            return
        
        # Clear previous trace
        self.trace_text.delete(1.0, tk.END)
        self.add_trace("=== AI ANALYZING BOARD ===\n", "header")
        self.add_trace(f"Current board state:\n{self.format_board()}\n\n", "info")
        
        # Find best move for AI with visualization
        bestMove = self.findBestMove(self.board)
        
        if bestMove[0] != -1:  # Valid move found
            row, col = bestMove
            self.board[row][col] = opponent
            self.buttons[row][col].config(text="O", fg="red", state="disabled")
            
            # Update best move display
            self.best_move_label.config(text=f"Best Move: ({row}, {col})")
            self.add_trace(f"\n>>> AI CHOSE: Position ({row}, {col}) <<<\n", "best")
            
            # Check if game is over after AI's move
            if self.check_game_over():
                return
        
        # Switch back to user's turn
        self.user_turn = True
        self.status_label.config(text="Your turn (X)", fg="green")
        self.eval_label.config(text="Your turn now", fg="green")
    
    def add_trace(self, text, tag=None):
        """Add text to the trace window"""
        if self.viz_var.get():
            self.trace_text.insert(tk.END, text, tag)
            self.trace_text.see(tk.END)
            self.root.update_idletasks()
    
    def format_board(self):
        """Format board for display in trace"""
        result = ""
        for i, row in enumerate(self.board):
            row_str = " | ".join([cell if cell != '_' else ' ' for cell in row])
            result += f"  {row_str}\n"
            if i < 2:
                result += "  ---------\n"
        return result
    
    def check_game_over(self):
        """Check if the game is over and display result"""
        score = self.evaluate(self.board)
        
        # Check for winner
        if score == 10:
            self.game_over = True
            self.status_label.config(text="You win!", fg="green")
            self.eval_label.config(text="Player wins!", fg="green")
            messagebox.showinfo("Game Over", "Congratulations! You won!")
            self.disable_all_buttons()
            return True
        elif score == -10:
            self.game_over = True
            self.status_label.config(text="AI wins!", fg="red")
            self.eval_label.config(text="AI wins!", fg="red")
            messagebox.showinfo("Game Over", "AI wins! Better luck next time.")
            self.disable_all_buttons()
            return True
        
        # Check for tie
        if not self.isMovesLeft(self.board):
            self.game_over = True
            self.status_label.config(text="It's a tie!", fg="purple")
            self.eval_label.config(text="It's a tie!", fg="purple")
            messagebox.showinfo("Game Over", "It's a tie!")
            self.disable_all_buttons()
            return True
        
        return False
    
    def disable_all_buttons(self):
        """Disable all board buttons when game is over"""
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state="disabled")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [
            ['_', '_', '_'],
            ['_', '_', '_'],
            ['_', '_', '_']
        ]
        self.game_over = False
        self.user_turn = True
        
        # Reset all buttons
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state="normal", bg="lightgray")
        
        self.status_label.config(text="Your turn (X)", fg="green")
        self.eval_label.config(text="Waiting for AI turn...")
        self.best_move_label.config(text="Best Move: --")
        self.trace_text.delete(1.0, tk.END)
    
    # Minimax algorithm functions with visualization
    def isMovesLeft(self, board):
        """Check if there are moves remaining on the board"""
        for i in range(3):
            for j in range(3):
                if (board[i][j] == '_'):
                    return True
        return False

    def evaluate(self, b):
        """Evaluate the current board state"""
        # Checking for Rows for X or O victory.
        for row in range(3):
            if (b[row][0] == b[row][1] and b[row][1] == b[row][2]):
                if (b[row][0] == player):
                    return 10
                elif (b[row][0] == opponent):
                    return -10

        # Checking for Columns for X or O victory.
        for col in range(3):
            if (b[0][col] == b[1][col] and b[1][col] == b[2][col]):
                if (b[0][col] == player):
                    return 10
                elif (b[0][col] == opponent):
                    return -10

        # Checking for Diagonals for X or O victory.
        if (b[0][0] == b[1][1] and b[1][1] == b[2][2]):
            if (b[0][0] == player):
                return 10
            elif (b[0][0] == opponent):
                return -10

        if (b[0][2] == b[1][1] and b[1][1] == b[2][0]):
            if (b[0][2] == player):
                return 10
            elif (b[0][2] == opponent):
                return -10

        # Else if none of them have won then return 0
        return 0

    def minimax(self, board, depth, isMax, visualize=False):
        """Minimax algorithm implementation with visualization"""
        score = self.evaluate(board)

        # If Maximizer has won the game return his/her evaluated score
        if (score == 10):
            return score - depth

        # If Minimizer has won the game return his/her evaluated score
        if (score == -10):
            return score + depth

        # If there are no more moves and no winner then it is a tie
        if (self.isMovesLeft(board) == False):
            return 0

        # If this maximizer's move
        if (isMax):
            best = -1000

            # Traverse all cells
            for i in range(3):
                for j in range(3):
                    # Check if cell is empty
                    if (board[i][j] == '_'):
                        # Make the move
                        board[i][j] = player

                        # Call minimax recursively and choose the maximum value
                        value = self.minimax(board, depth + 1, not isMax)
                        best = max(best, value)

                        # Undo the move
                        board[i][j] = '_'
            return best

        # If this minimizer's move
        else:
            best = 1000

            # Traverse all cells
            for i in range(3):
                for j in range(3):
                    # Check if cell is empty
                    if (board[i][j] == '_'):
                        # Make the move
                        board[i][j] = opponent

                        # Call minimax recursively and choose the minimum value
                        value = self.minimax(board, depth + 1, not isMax)
                        best = min(best, value)

                        # Undo the move
                        board[i][j] = '_'
            return best

    def findBestMove(self, board):
        """Find the best possible move for the AI with visualization"""
        bestVal = 1000  # AI is minimizer, so we want the minimum value
        bestMove = (-1, -1)
        
        move_count = 0

        # Traverse all cells, evaluate minimax function for all empty cells
        for i in range(3):
            for j in range(3):
                # Check if cell is empty
                if (board[i][j] == '_'):
                    move_count += 1
                    
                    # Make the move
                    board[i][j] = opponent
                    
                    self.add_trace(f"\nEvaluating move ({i}, {j})...\n", "move")
                    
                    # compute evaluation function for this move
                    moveVal = self.minimax(board, 0, True)
                    
                    self.add_trace(f"  Score: {moveVal}\n", "score")
                    
                    # Undo the move
                    board[i][j] = '_'

                    # If the value of the current move is less than the best value, update best
                    if (moveVal < bestVal):
                        bestMove = (i, j)
                        bestVal = moveVal
                        self.add_trace(f"  >>> New best move! <<<\n", "best")
                    
                    # Update evaluation label
                    self.eval_label.config(
                        text=f"Evaluated {move_count} moves | Best score: {bestVal}"
                    )
                    self.root.update_idletasks()

        return bestMove

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGame(root)
    root.mainloop()