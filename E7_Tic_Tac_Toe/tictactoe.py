import tkinter as tk
from tkinter import messagebox
import numpy as np

# Player and opponent constants
player, opponent = 'x', 'o'

class TicTacToeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe: You vs AI")
        self.root.geometry("500x500")
        self.root.resizable(True, True)
        
        # Initialize game state
        self.board = [
            ['_', '_', '_'],
            ['_', '_', '_'],
            ['_', '_', '_']
        ]
        
        self.game_over = False
        self.user_turn = True  # User starts first
        
        # Create UI elements
        self.create_widgets()
        
        # If AI should start first, uncomment the next line
        # self.ai_move()
    
    def create_widgets(self):
        # Title label
        title_label = tk.Label(self.root, text="Tic-Tac-Toe", 
                               font=("Arial", 24, "bold"), fg="blue")
        title_label.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Your turn (X)", 
                                    font=("Arial", 14), fg="green")
        self.status_label.pack(pady=5)
        
        # Game board frame
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=20)
        
        # Create buttons for the board
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    board_frame,
                    text="",
                    font=("Arial", 32, "bold"),
                    width=4,
                    height=2,
                    bg="lightgray",
                    command=lambda row=i, col=j: self.user_move(row, col)
                )
                self.buttons[i][j].grid(row=i, column=j, padx=5, pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)
        
        # Reset button
        reset_button = tk.Button(control_frame, text="Reset Game", 
                                font=("Arial", 12), 
                                command=self.reset_game,
                                bg="lightblue", width=15)
        reset_button.grid(row=0, column=0, padx=10)
        
        # Exit button
        exit_button = tk.Button(control_frame, text="Exit", 
                               font=("Arial", 12), 
                               command=self.root.quit,
                               bg="lightcoral", width=15)
        exit_button.grid(row=0, column=1, padx=10)
        
        # Instructions label
        instructions = tk.Label(self.root, 
                               text="You are X, AI is O. Click a cell to make your move.",
                               font=("Arial", 10), fg="gray")
        instructions.pack(pady=10)
    
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
            
        # Find best move for AI
        bestMove = self.findBestMove(self.board)
        
        if bestMove[0] != -1:  # Valid move found
            row, col = bestMove
            self.board[row][col] = opponent
            self.buttons[row][col].config(text="O", fg="red", state="disabled")
            
            # Check if game is over after AI's move
            if self.check_game_over():
                return
        
        # Switch back to user's turn
        self.user_turn = True
        self.status_label.config(text="Your turn (X)", fg="green")
    
    def check_game_over(self):
        """Check if the game is over and display result"""
        score = self.evaluate(self.board)
        
        # Check for winner
        if score == 10:
            self.game_over = True
            self.status_label.config(text="You win!", fg="green")
            messagebox.showinfo("Game Over", "Congratulations! You won!")
            self.disable_all_buttons()
            return True
        elif score == -10:
            self.game_over = True
            self.status_label.config(text="AI wins!", fg="red")
            messagebox.showinfo("Game Over", "AI wins! Better luck next time.")
            self.disable_all_buttons()
            return True
        
        # Check for tie
        if not self.isMovesLeft(self.board):
            self.game_over = True
            self.status_label.config(text="It's a tie!", fg="purple")
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
    
    # Minimax algorithm functions
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

    def minimax(self, board, depth, isMax):
        """Minimax algorithm implementation"""
        score = self.evaluate(board)

        # If Maximizer has won the game return his/her evaluated score
        if (score == 10):
            return score

        # If Minimizer has won the game return his/her evaluated score
        if (score == -10):
            return score

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
                        best = max(best, self.minimax(board, depth + 1, not isMax))

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
                        best = min(best, self.minimax(board, depth + 1, not isMax))

                        # Undo the move
                        board[i][j] = '_'
            return best

    def findBestMove(self, board):
        """Find the best possible move for the AI"""
        bestVal = 1000  # AI is minimizer, so we want the minimum value
        bestMove = (-1, -1)

        # Traverse all cells, evaluate minimax function for all empty cells
        for i in range(3):
            for j in range(3):
                # Check if cell is empty
                if (board[i][j] == '_'):
                    # Make the move
                    board[i][j] = opponent

                    # compute evaluation function for this move
                    moveVal = self.minimax(board, 0, True)

                    # Undo the move
                    board[i][j] = '_'

                    # If the value of the current move is less than the best value, update best
                    if (moveVal < bestVal):
                        bestMove = (i, j)
                        bestVal = moveVal

        return bestMove

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGame(root)
    root.mainloop()