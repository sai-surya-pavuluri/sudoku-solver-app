class SudokuSolver:
    def __init__(self, board):
        board = [[str(cell) if cell != '' else '' for cell in row] for row in board]
        self.board = board

    def solve(self):
        if self.sudoku_solver(self.board):
            return self.board
        else:
            return None

    def sudoku_solver(self, board, row=0, col=0):
        if row == 9:
            return True
        nextRow = row
        nextCol = col + 1
        if nextCol == 9:
            nextRow += 1
            nextCol = 0
        if board[row][col] != '':
            return self.sudoku_solver(board, nextRow, nextCol)
        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = str(num)
                if self.sudoku_solver(board, nextRow, nextCol):
                    return True
                board[row][col] = ''
        return False

    def is_valid(self, board, row, col, num):
        num = str(num)
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        startRow = (row // 3) * 3
        startCol = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[startRow + i][startCol + j] == num:
                    return False
        return True
