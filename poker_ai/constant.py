###############################################
# Constant:

DEBUG_MODE=1
# Turn on for better visibility

MODEL=-1
# Choose AI module for all bot in a normal game for main.py:
# 0: simple rule-based AI using probability theorem, game-based rule and some randomness
# 1: super randomized AI
# 2: my friend's AI who shove all in every game and play by pure luck
STOP = 0
# 0 for stop after every game, 1 to skip stop
PREFLOP_BIG_BLIND = 10
# Value of the big blind pre-bet.
INDICATOR = 1
# 0 is for testing against all human-controlled
# 1 is for bot: Player 1 will be human, all others will be bot
# 2 is all bot for testing purpose
MULTIPROCESS = 1
# 0 is for single-processing, slower
# 1 is for multi-processing, faster and recommended
TURN_TO_RAISE_POT = 5
# Number of turns to increase the big blind pre-bet

CONFIDENT_RANGE = 0.25
# should be < 0.5
RISK_RANGE=0.95
# The range so that the AI should just all in because it's card is high enough and they don't have much money left
DRAW=0.7
WIN=0.6
CALL_RANGE=0.05
BLUFF_RANGE=(0.05,0.1)
BLUFF_INCREASE=0.7
RULE_DICT={0:0.85,3:0.9,4:0.95,5:1}
BETTED_DICT={0:1,1:0.95}
OPPONENT_CONFIDENT_RANGE={1:(0.05,-0.05),2:(-0.1,-0.1),3:(-0.2,-0.05),4:(-0.1,0.5),5:(-0.15,0.3),6:(-0.2,0.2),8:(-0.3,0.1)}

PLAYER = 6
INIT_MONEY = 50 * PREFLOP_BIG_BLIND

DEEPNESS = 5000
# The number of iterations of the Monte-Carlo simulation. Higher is better but requires more time and memory
# Recommended deepness: 1000 for single or test/battery saver, 5000 for multi and playing
CONFIDENT_RATE = 0.8
# The base confident_rate of a player, represent the chance that the player will check/call in a 2 player games
# Don't ask where I get this number, it's taken by testing a lot

# constants for opponent modelling
RESCALING_SIZE = 8

################################################
