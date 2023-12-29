# Poker AI for capstone project
----------------
This project contains best effort open source implementation of a poker AI using several methods. The AI models are built by simple rule-based method + simulations, Monte-Carlo tree search and opponent modeling. The game is built mainly on terminal, but we also have a pygame expansion for playing against bots.

# Note: This project is just for education purpose. We do not encourage gambling, as it is illegal here in Vietnam. We do not hold responsibility for any misuse of this programs. 

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
Note that:
  - The pygame implement only support games of player vs AIs. It currently do not support player vs players and AI vs AIs, since it's
impossible for players to play in 1 machine and AI games are faster on terminal.
  - The game logs and many useful informations is printed out in the terminal.

## Training your own opponent modeling model:
- Firstly, you should make a backup file of poker_ai/ai/ml/default_data.json, as it is our model's default data.
- To start off, delete/rename the default_data.json.
- Run training.py:
```bash
python training.py #mode
```
All of the modes for traning:
  - 1: Best suited for model againts 2 players.
  - 2: Best suited for model againts 3-4 players.
  - 3: Best suited for model againts 5-6 players.
  - 4: Best suited for model againts 2-6 players.
Note that the opponent modeling is only useful with enough training time, with the minimum should be 2-3 hours. If you don't have much time, please use our pre-trained model.

## Tesing the AI against each others:
- Edit tester.py:
```python
if __name__=="__main__":
    game_loop_model_test(num_players,init_money,games,models_list)
```
Changes the parameters:
  - num_players: number of player in testing
  - init_money: the amount of starting money
  - games: the number of games to test
  - models_list: the models that you want to use in the test. The first element will be Player 1's model, second will be Player 2's model and so on.
- Run training.py:
```bash
python tester.py
```
- After testing, the file will print out the number of games win by every players.

## Note:
  - The multiprocessing has a strange interaction with KeyboardInterrupt. As such, if not necessary, don't try to cancel any running programs with multiprocessing running. The best bet to cancel any programs is when it's your turn to act in a player vs AI mode.
  - All of the materials and references we used in this project is inside books & materials folders.