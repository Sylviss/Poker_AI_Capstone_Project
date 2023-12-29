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
<p align="center">
  <img src="https://github.com/Sylviss/Poker_AI_Capstone_Project/blob/main/doc/play_constant.PNG">
</p>

## The simple roadmap:
- [x] Simple warmup and learn to use Github
- [x] Find some material
- [x] Implement the basic UI and game structure
- [ ] Implement the AI:
    - [x] Implement the evaluate function using simple Monte-Carlo simulations
    - [x] Implement the Monte-Carlo simulation/rule-based and enumeration/rule-based AI
    - [X] Implement the Monte-Carlo tree search-based AI
    - [ ] Implement a supervised learning for opponent modelling for all of the AI:
      - [ ] For the simulation/rule-based AI:
        - [ ] Improve the simulations so that it is not just straight all-in simulations.
        - [ ] Using opponent modelling to implement enumeration weighting, improving the CALL_CONFIDENT and the simulation itself (2.5.2.4, 2.6)
        - [ ] After enumeration weighting, use selective sampling to only simulate cases that have high weight to be relevant.
        - [ ] Implement adaptive sampling based on the current game state, opponents' behaviors, or other relevant factors.
      - [ ] For the enumeration/rule-based AI:

      - [ ] For the MCTS AI:
        - [ ] Implement the opponent modelling as the main selection policy for the AI.
- [ ] Implement a performance evaluation
- [x] Drink some water
- [x] Touch the grass

Try ur best.

