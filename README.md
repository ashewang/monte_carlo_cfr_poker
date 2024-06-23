# Group Members
| No. | Name          | ID           |
|-----|---------------|--------------|
| 1   | Yared Tsegaye | UGR/8284/12  |
| 2   | Elsai Deribu  | UGR/0066/12  |


# Poker AI Simulation

This repository contains the implementation of a Poker AI using Monte Carlo Counterfactual Regret Minimization (MCCFR) techniques. The code simulates learning strategies using self play for a simplified version of poker, including both Leduc and Kuhn variants.

## Overview

The project utilizes several Python files for managing game states, actions, card evaluations, and utilities. The main execution starts from the `learn` function which simulates learning and self play iterations for optimal poker strategies.

## Dependencies

- Python 3.x
- NumPy
- tqdm (for progress bars)

## Files Description

- `card.py`: Defines the `Card` class which represents a playing card.
- `node.py`: Defines the `MNode` class for managing game states in the CFR algorithm.
- `hand_eval.py`: Contains functions `leduc_eval` and `kuhn_eval` for evaluating hand strengths in Leduc and Kuhn poker variants.
- `util.py`: Includes utility functions such as `expected_utility` and `bias`.
- `best_response.py`: Contains the `exploitability` function to calculate how far a strategy is from being unexploitable.
- `state.py`: Contains classes `Leduc` and `State` for managing different game states.

## Usage

To run the simulation, make sure all dependencies are installed and execute:
1. Clone the repository
```bash
git clone https://github.com/Yared-betsega/monte-carlo-cfr-poker.git
```

2. Navigate to the the clone repository
```bash
cd monte-carlo-cfr-poker
```

3. Install necessary packages
```bash
pip install -r requirements.txt
```
4. After this there are two files to run
- Run the mccfr learning process. This will print out all the available states in the game and their calculated strategies(Probabilities) for optimal nash equilibrium play.
```bash
python monte_carlo_cfr.py 
```

- Run the search simulation on the terminal. (Simulation for real time playing). This will let you play the simple version of the game in the terminal. 
```bash
python search.py
