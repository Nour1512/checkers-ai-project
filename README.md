# Checkers AI (Minimax + Alpha-Beta)

A Python-based implementation of the classic **Checkers (Draughts)** game featuring an intelligent AI opponent built using the **Minimax algorithm** with **Alpha-Beta pruning** for optimized decision-making.

---

##  Features

* Full 8x8 Checkers game implementation
* Legal move generation with **forced captures**
* Support for **multi-jump (chain captures)**
* **King promotion** system
* AI powered by:

  * Minimax Algorithm
  * Alpha-Beta Pruning
* Heuristic evaluation based on:

  * Piece count
  * King value
  * Mobility
* Multiple game modes:

  * Human vs AI
  * AI vs AI
  * Human vs Human
* Console gameplay
* Optional **Pygame GUI**

---

##  AI Overview

The AI evaluates possible future game states using:

* **Minimax Search** to simulate opponent moves
* **Alpha-Beta Pruning** to reduce unnecessary computations
* A custom **evaluation function** that scores board positions

This allows the AI to make strong and efficient decisions even at deeper search levels.

---

##  Game Modes

| Mode           | Description                      |
| -------------- | -------------------------------- |
| Human vs AI    | Play against the AI              |
| AI vs AI       | Watch two AI agents compete      |
| Human vs Human | Play locally with another player |

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/checkers-ai.git
cd checkers-ai
```

### 2. Install dependencies (for GUI)

```bash
pip install pygame
```

---

## ▶ Running the Game

```bash
python checkers_ai.py
```

You will be prompted to choose a mode:

```
1) Human vs AI
2) AI vs AI
3) Human vs Human
```

---

##  Configuration

* Default AI depth: **6**
* Increase depth for stronger AI (but slower performance)

You can modify it directly when running the program.

---

##  Project Structure

```
checkers_ai.py
```

Main components:

* `Board` → Game state representation
* `Move Generation` → Legal moves and captures
* `MinimaxAgent` → AI logic
* `Evaluation Function` → Board scoring
* `PygameUI` → Optional graphical interface

---

##  GUI (Optional)

If `pygame` is installed, the game can run with a graphical interface:

* Click pieces to select moves
* Visual hints for legal moves
* Smooth interactive gameplay

---

##  Concepts Used

* Game Trees
* Adversarial Search
* Recursion
* Heuristic Design
* Optimization (Alpha-Beta Pruning)

---

##  Future Improvements

* Reinforcement Learning (self-play training)
* Better evaluation heuristics
* Online multiplayer
* Improved UI/UX

---

## 👤 Author

**Nour Nader Mohamed**
