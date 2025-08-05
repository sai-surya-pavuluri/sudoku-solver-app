import { useState } from 'react'
import React from 'react';
import Confetti from "react-confetti";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import './App.css'

function App() {
  const [board, setBoard] = useState(Array(9).fill().map(() => Array(9).fill('')))
  const [showConfetti, setShowConfetti] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isSolved, setIsSolved] = useState(false);

  const handleInputChange = (r, c, val) => {
    if (!/^[1-9]?$/.test(val)) return;
    const newBoard = board.map((row, i) =>
      row.map((cell, j) => (i === r && j === c ? val : cell))
    );
    setBoard(newBoard);
  };

  const getBlockClass = (r, c) => {
    const blockRow = Math.floor(r / 3);
    const blockCol = Math.floor(c / 3);
    const blockIndex = blockRow * 3 + blockCol;
    const blockNames = ['block-a', 'block-b', 'block-c',
                        'block-b', 'block-c', 'block-a',
                        'block-c', 'block-a', 'block-b'];
    return blockNames[blockIndex];
  };

  const handleClear = () => {
    setBoard(Array(9).fill().map(() => Array(9).fill("")));
    setIsSolved(false);
  };

  const triggerFireworks = () => {
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 3000);
  };

  const handleSolve = async () => {
    try {
      setLoading(true);
      const toastId = toast.loading("Solving the Sudoku...");
      const response = await fetch("http://localhost:5000/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ board })
      });

      const data = await response.json();
      if (data.success) {
        setLoading(false);
        setIsSolved(true);
        setBoard(data.solution);
        toast.update(toastId, {
          render: "Solved successfully!",
          type: "success",
          isLoading: false,
          autoClose: 2000
        });
        triggerFireworks();
      } else {
        setLoading(false);
        toast.update(toastId, {
          render: "Could not solve the puzzle. Please check your input.",
          type: "error",
          isLoading: false,
          autoClose: 2000
        });
      }
    } catch (err) {
      setLoading(false);
      toast.error("An error occurred while solving the Sudoku.", {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }
  };

const handleImageUpload = async (event) => {
  try {
    const toastId = toast.loading("Extracting puzzle from image...");
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("sudoku_image", file);

    const response = await fetch("http://localhost:5000/api/upload-sudoku", {
      method: "POST",
      body: formData,
    });

    const { puzzle } = await response.json();

    const newBoard = Array(9).fill().map(() => Array(9).fill(''));
    for (const key in puzzle) {
      const [r, c] = key.split(',').map(Number);
      newBoard[r][c] = puzzle[key];
    }

    setBoard(newBoard);
    toast.update(toastId, {
      render: "Puzzle extracted successfully!",
      type: "success",
      isLoading: false,
      autoClose: 2000
    });
  } catch (err) {
    toast.error("Failed to extract puzzle from image. Try another one.");
  }
};



return (
    <div className="sudoku-container">
      <h1>Sudoku Solver</h1>
      <div className="sudoku-board">
        {board.map((row, rowIndex) => (
          row.map((value, colIndex) => (
            <input
              key={`${rowIndex}-${colIndex}`}
              type="text"
              maxLength={1}
              value={value}
              onChange={(e) =>
                handleInputChange(rowIndex, colIndex, e.target.value)
              }
              className={`sudoku-cell ${getBlockClass(rowIndex, colIndex)}`}
              disabled={loading || isSolved}
            />
          ))
        ))}
      </div>
      <div className="buttons">
        <button className='reset-button' onClick={handleClear} disabled={loading}>Reset</button>
        <button className='solve-button' onClick={handleSolve} disabled={loading || isSolved}>Solve</button>
        <label htmlFor="file-upload" className="upload-label">
          Upload Sudoku
        </label>
        <input
          id="file-upload"
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ display: "none" }}
        />
      </div>

      {showConfetti && <Confetti />}
      <ToastContainer />

    </div>
  );
}

export default App
