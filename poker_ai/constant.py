
###############################################
# Constant:

DEBUG_MODE=1
# Turn on for better visibility

MODEL=0
# Choose AI module for all bot in a normal game for main.py:
# 0: simple rule-based AI using probability theorem, game-based rule and some randomness
# 1: super randomized AI
# 2: my friend's AI who shove all in every game and play by pure luck
STOP = 0
# 0 for stop after every game, 1 to skip stop
PREFLOP_BIG_BLIND = 10
# Value of the big blind pre-bet.
INDICATOR = 2
# 0 is for testing against all human-controlled
# 1 is for bot: Player 1 will be human, all others will be bot
# 2 is all bot for testing purpose
MULTIPROCESS = 1
# 0 is for single-processing, slower
# 1 is for multi-processing, faster and recommended
TURN_TO_RAISE_POT = 5
# Number of turns to increase the big blind pre-bet

DECIDER = 10
CONFIDENT_RANGE = 0.3  
# should be < 0.5
RISK_RANGE=0.95
# The range so that the AI should just all in because it's card is high enough and they don't have much money left
DRAW=0.7
WIN=0.6
CALL_RANGE=0.05
BLUFF_RANGE=(0.05,0.1)
BLUFF_INCREASE=0.7

PLAYER = 5
INIT_MONEY = 50 * PREFLOP_BIG_BLIND


DEEPNESS = 5000
# The number of iterations of the Monte-Carlo simulation. Higher is better but requires more time and memory
# Recommended deepness: 5000 for single or test/battery saver, 10000 for multi and playing
CONFIDENT_RATE = 0.8
# The base confident_rate of a player, represent the chance that the player will check/call in a 2 player games
# Don't ask where I get this number, it's taken by testing a lot
################################################