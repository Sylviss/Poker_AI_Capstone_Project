# Poker AI for capstone project
----------------
This project contains best effort open source implementation of a poker AI using several methods. The AI models are built by simple rule-based method + simulations, Monte-Carlo tree search and opponent modeling. The game is built mainly on terminal, but we also have a pygame expansion for playing against bots. 
# Installation & running guide:
## Prerequisites:
This repository assumes Python 3.11 or newer is used.
Used package:
- bext
- colorama
- pygame

## Installation guide:
- Clone the repo to your own machine:
```bash
git clone 
```

## Run the game:
- Firstly, you should change some constant in poker_ai/constant.py:
```python
PLAYER = 2
# The number of players
PREFLOP_BIG_BLIND = 10
# Value of the big blind pre-bet.
INIT_MONEY = 50 * PREFLOP_BIG_BLIND
# The starting money of all players
STOP = 0
# 0 for stop after every game, 1 to skip stop
INDICATOR = 1
# 0 is for testing against all human-controlled
# 1 is for human vs bots: Player 1 will be human, all others will be bot
# 2 is all bots for testing purpose
MULTIPROCESS = 1
# 0 is for single-processing, slower. You should use this if you encounter some problems with multiprocessing.
# 1 is for multi-processing, faster and recommended.
MODEL=7
# Choose AI module for all bot in a normal game for main.py:
# -1: enumeration ai agent
# 0: first approach mcs ai agent
# 1: second approach mcs ai agent
# 2: mcts ai agent
# 3: all in ai agent
# 4: super random ai agent
# 5: first approach mcs ai agent with opponent modeling
# 6: second approach mcs ai agent with opponent modeling
# 7: mcts ai agent with opponent modeling
# Note that opponent modeling is implemented with multiprocess, so don't use opponent modeling if you encounter some problems with multiprocessing.
```
- Running main.py will run the game in terminal with all of the above settings:
```bash
python main.py
```
- If you want to play the game in a fancy pygame implement, run fancy_rable.py:
```bash
python fancy_table.py
```
Note that 