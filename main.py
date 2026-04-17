from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI()

class Move(BaseModel):
    row: int
    col: int

class GameState(BaseModel):
    board: List[List[Literal['X', 'O', '']]]
    current_player: Literal['X', 'O']
    winner: Literal['X', 'O', 'Draw', None]
    is_game_over: bool

# Initial game state
_game_state = GameState(
    board=[['', '', ''], ['', '', ''], ['', '', '']],
    current_player='X',
    winner=None,
    is_game_over=False
)

def _check_winner(board: List[List[str]]) -> Literal['X', 'O', None]:
    # Check rows
    for row in board:
        if row[0] != '' and row[0] == row[1] == row[2]:
            return row[0]
    # Check columns
    for col in range(3):
        if board[0][col] != '' and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    # Check diagonals
    if board[0][0] != '' and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != '' and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None

def _check_draw(board: List[List[str]]) -> bool:
    for row in board:
        if '' in row:
            return False
    return True

@app.get("/game", response_model=GameState)
async def get_game_state():
    """Get the current state of the Tic Tac Toe game."""
    return _game_state

@app.post("/game/move", response_model=GameState)
async def make_move(move: Move):
    """Make a move in the Tic Tac Toe game."""
    global _game_state

    if not (0 <= move.row < 3 and 0 <= move.col < 3):
        raise HTTPException(status_code=400, detail="Invalid row or column.")

    if _game_state.is_game_over:
        raise HTTPException(status_code=400, detail="Game is already over. Please reset to play again.")

    if _game_state.board[move.row][move.col] != '':
        raise HTTPException(status_code=400, detail="Cell is already occupied.")

    # Apply move
    _game_state.board[move.row][move.col] = _game_state.current_player

    # Check for winner
    winner = _check_winner(_game_state.board)
    if winner:
        _game_state.winner = winner
        _game_state.is_game_over = True
    else:
        # Check for draw
        if _check_draw(_game_state.board):
            _game_state.winner = "Draw"
            _game_state.is_game_over = True
        else:
            # Switch player
            _game_state.current_player = 'O' if _game_state.current_player == 'X' else 'X'
    
    return _game_state

@app.post("/game/reset", response_model=GameState)
async def reset_game():
    """Reset the Tic Tac Toe game to its initial state."""
    global _game_state
    _game_state = GameState(
        board=[['', '', ''], ['', '', ''], ['', '', '']],
        current_player='X',
        winner=None,
        is_game_over=False
    )
    return _game_state

# You can run this file using: `uvicorn main:app --reload`

# For allowing CORS during local development, uncomment the following:
# from fastapi.middleware.cors import CORSMiddleware
# origins = [
#     "http://localhost",
#     "http://localhost:8000",
#     "http://127.0.0.1:5500", # If using Live Server extension
#     # Add any other origins where your frontend might be hosted
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()
