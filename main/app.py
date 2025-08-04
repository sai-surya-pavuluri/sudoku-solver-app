from flask import Flask, request, jsonify, render_template
import os
import logging
from sudoku_solver import SudokuSolver as sudoku_solver


logging.basicConfig(
    level=logging.INFO,  # Or WARNING/ERROR/DEBUG
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
        template_folder=os.path.abspath("templates"),
        static_folder=os.path.abspath("static"),
        static_url_path="" 
)

@app.route('/')
def index():
    """
    Render the main page of the Sudoku solver app.
    """
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    logger.info("Received request to solve Sudoku puzzle.")
    data = request.get_json()
    if not data or 'board' not in data:
        logger.error("Invalid request data.")
        return jsonify({'error': 'Invalid request data'}), 400
    
    board = data['board']
    if not isinstance(board, list) or len(board) != 9 or any(len(row) != 9 for row in board):
        logger.error("Invalid Sudoku board format.")
        return jsonify({'error': 'Invalid Sudoku board format'}), 400
    logger.info("Starting Sudoku solving process.")
    
    solver = sudoku_solver(board)
    solved_board = solver.solve()
    logger.info(f"Sudoku solver output: {solved_board}")

    if solved_board is not None:
        logger.info("Sudoku puzzle solved successfully.")
        return jsonify({'success': True, 'solution': solved_board})
    else:
        logger.error("Failed to solve Sudoku puzzle.")
        return jsonify({'error': 'Failed to solve Sudoku puzzle'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    logger.info("Starting the Sudoku solver app.")
    app.run(debug=True, host='0.0.0.0', port=5000)