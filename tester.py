from collections import defaultdict
from poker_ai.poker.play import fast_testing
import sys,os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w', encoding="utf-8")

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def main():
    try:
        d = defaultdict(lambda: 0)
        for t in range(10):
            blockPrint()
            d[fast_testing(2,100,[0,1])] += 1
            enablePrint()
            print(t)
        for key in d:
            print(f'{key}: {d[key]}')
    except KeyboardInterrupt:
        sys.exit()
        
if __name__=="__main__":
    main()
