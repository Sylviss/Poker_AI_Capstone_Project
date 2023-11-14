from poker_ai.poker.play import game
import sys
from poker_ai.constant import PLAYER,INIT_MONEY


def main():
    try:
        game(PLAYER,INIT_MONEY)
    except KeyboardInterrupt:
        sys.exit()
        
if __name__=="__main__":
    main()
