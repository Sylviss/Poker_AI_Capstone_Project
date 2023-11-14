from collections import defaultdict
from poker_ai.poker.play import game
import bext,sys

def main():
    try:
        d = defaultdict(lambda: 0)
        for _ in range(50):
            d[game(2,100)] += 1

        bext.clear()
        for key in d:
            print(f'{key}: {d[key]}')
    except KeyboardInterrupt:
        sys.exit()
        
if __name__=="__main__":
    main()
