from poker_ai.poker.play import game_loop, game_loop_model_test
import sys
from poker_ai.constant import PLAYER,INIT_MONEY


def main():
    try:
        game_loop(PLAYER, INIT_MONEY)
    except KeyboardInterrupt:
        sys.exit()
        
if __name__=="__main__":
    main()
