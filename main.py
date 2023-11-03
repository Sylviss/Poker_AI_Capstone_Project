from poker_ai.poker.play import game,PREFLOP_BIG_BLIND
import sys


###############################################
#Constant:

PLAYER=3
INIT_MONEY=10*PREFLOP_BIG_BLIND


################################################

try:
    game(PLAYER,INIT_MONEY)
except KeyboardInterrupt:
    sys.exit()
