# Matrix Calculator

A refactored Python GUI calculator for core vector and matrix operations.

## Refactor Notice

This repository has been refactored with the help of AI Copilot (GitHub Copilot).

- The current codebase is the actively maintained version.
- To review the original implementation history, see older commits in this repository.
- The full previous README has been preserved as legacy documentation in [README_OLD.md](README_OLD.md).

## Overview

This project provides a Tkinter-based desktop interface for common linear algebra workflows:

- Vector operations (addition, subtraction, dot product, cross product, scalar multiply, angle/properties)
- Matrix operations (addition, subtraction, multiplication, scalar multiplication, transpose, Gaussian elimination)

The current implementation separates UI flow from operation logic for better maintainability and testing.

## Tech Stack

- Python 3.12+
- Tkinter/ttk for GUI
- Pytest for tests

## Run the Current Project

### 1. Clone and enter the repository

```bash
git clone git@github.com:omkar-thite/matrix_calculator.git
cd matrix_calculator
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e .
```

### 4. Launch the GUI

```bash
python main.py
```

## Run Tests

```bash
pytest
```

## Project Structure (Current)

- `main.py`: Tkinter app entry point and UI flow controller
- `operation_services.py`: parsing and operation service functions
- `vector/vector.py`: vector and matrix domain models
- `tests/`: automated test suite

## Documentation (Older Version)

The section below is from the older version of the project and is kept for historical reference.

For the complete original README content, see [README_OLD.md](README_OLD.md).
  




     
    







  

  

  









