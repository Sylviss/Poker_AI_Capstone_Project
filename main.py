from poker_ai.poker.play import game,PREFLOP_BIG_BLIND

from poker_ai.ai.eval_func import eval_func,multi_process_eval_func
from poker_ai.poker.poker_component import Player,Hand,Deck,Card
import time

import sys


###############################################
#Constant:

PLAYER=6
INIT_MONEY=10*PREFLOP_BIG_BLIND


################################################
def main():
    try:
        game(PLAYER,INIT_MONEY)
    except KeyboardInterrupt:
        sys.exit()
        
if __name__=="__main__":
    main()
