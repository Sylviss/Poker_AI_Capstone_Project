from collections import defaultdict
from poker_ai.poker.play import fast_testing,game_but_cheaty
import sys,os

# Disable print
def blockPrint():
    sys.stdout = open(os.devnull, 'w', encoding="utf-8")

# Restore print
def enablePrint():
    sys.stdout = sys.__stdout__

def test_win_rate(n):
    try:
        d = defaultdict(lambda: 0)
        for t in range(n):
            blockPrint()
            d[fast_testing(2,100,[0,1])] += 1
            enablePrint()
            print(t)
        for key in d:
            print(f'{key}: {d[key]}')
    except KeyboardInterrupt:
        sys.exit()
        
def test_hacker():
    try:
        game_but_cheaty(2,500,["4s","4d","Ad","10s","As","10d","4h","Ac","4c"])
    except KeyboardInterrupt:
        sys.exit()
        
def test_single_game():
    print(fast_testing(5,500,[0,1,1,1,1]))
    

if __name__=="__main__":
    test_win_rate(50)
