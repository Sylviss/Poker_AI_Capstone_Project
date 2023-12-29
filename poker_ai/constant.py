###############################################
# Constant for playing the game:

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


###############################################
# Constant:

DEBUG_MODE=1
# Turn on for better visibility
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
BETTED=0.95
OPPONENT_CONFIDENT_RANGE={1:(0.05,-0.05),2:(-0.1,-0.1),3:(-0.2,-0.05),4:(-0.1,0.5),5:(-0.15,0.3),6:(-0.2,0.2),8:(-0.3,0.1)}
UPDATE_WEIGHT=0.5
UBC1_CONSTANT=1.3

DEEPNESS = 5000
# The number of iterations of the Monte-Carlo simulation. Higher is better but requires more time and memory
# Recommended deepness: 1000 for single or test/battery saver, 5000 for multi and playing
CONFIDENT_RATE = 0.8
# The base confident_rate of a player, represent the chance that the player will check/call in a 2 player games
# Don't ask where I get this number, it's taken by testing a lot

color = {
	'ResetAll' : "\033[0m",

	'Bold'       : "\033[1m",
	'Dim'        : "\033[2m",
	'Underlined' : "\033[4m",
	'Blink'      : "\033[5m",
	'Reverse'    : "\033[7m",
	'Hidden'     : "\033[8m",

	'ResetBold'       : "\033[21m",
	'ResetDim'        : "\033[22m",
	'ResetUnderlined' : "\033[24m",
	'ResetBlink'      : "\033[25m",
	'ResetReverse'    : "\033[27m",
	'ResetHidden'     : "\033[28m",

	'Default'      : "\033[39m",
	'Black'        : "\033[30m",
	'Red'          : "\033[31m",
	'Green'        : "\033[32m",
	'Yellow'       : "\033[33m",
	'Blue'         : "\033[34m",
	'Magenta'      : "\033[35m",
	'Cyan'         : "\033[36m",
	'LightGray'    : "\033[37m",
	'DarkGray'     : "\033[90m",
	'LightRed'     : "\033[91m",
	'LightGreen'   : "\033[92m",
	'LightYellow'  : "\033[93m",
	'LightBlue'    : "\033[94m",
	'LightMagenta' : "\033[95m",
	'LightCyan'    : "\033[96m",
	'White'        : "\033[97m",

	'BackgroundDefault'      : "\033[49m",
	'BackgroundBlack'        : "\033[40m",
	'BackgroundRed'          : "\033[41m",
	'BackgroundGreen'        : "\033[42m",
	'BackgroundYellow'       : "\033[43m",
	'BackgroundBlue'         : "\033[44m",
	'BackgroundMagenta'      : "\033[45m",
	'BackgroundCyan'         : "\033[46m",
	'BackgroundLightGray'    : "\033[47m",
	'BackgroundDarkGray'     : "\033[100m",
	'BackgroundLightRed'     : "\033[101m",
	'BackgroundLightGreen'   : "\033[102m",
	'BackgroundLightYellow'  : "\033[103m",
	'BackgroundLightBlue'    : "\033[104m",
	'BackgroundLightMagenta' : "\033[105m",
	'BackgroundLightCyan'    : "\033[106m",
	'BackgroundWhite'        : "\033[107m"
}

# constants for opponent modelling
RESCALING_SIZE = 20

################################################
