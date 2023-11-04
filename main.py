from poker_ai.poker.play import game,PREFLOP_BIG_BLIND
import sys


###############################################
#Constant:

PLAYER=4
INIT_MONEY=10*PREFLOP_BIG_BLIND


################################################
def main():
    for _ in range(10):
        try:
            game(PLAYER,INIT_MONEY)
        except KeyboardInterrupt:
            sys.exit()
        
if __name__=="__main__":
    main()
