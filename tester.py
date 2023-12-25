from collections import defaultdict
from poker_ai.poker.play import fast_testing,game_but_cheaty
import sys,os
from test import main
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
            # blockPrint()
            d[fast_testing(2,1000,[1,2])] += 1
            # enablePrint()
            print(t)
        for key in d:
            print(f'{key}: {d[key]}')
    except KeyboardInterrupt:
        sys.exit()
        
def test_hacker():
    try:
        game_but_cheaty(2,2000,["4s","4d","Ad","As","10s","10d","Ac","4h","4c"])
        # game_but_cheaty(2,500,["Ad","As","4s","4d","10s","10d","Ac","4h","4c"])
    except KeyboardInterrupt:
        sys.exit()
        
def test_single_game():
    test_hacker()
    
def test_module():
    fast_testing(2,100,[1,1])
    
    
def training(n):
    if n==2:
        hehe=[1,-1]
    elif n==4:
        hehe=[1,0,-1,-1]
    else:
        hehe=[1,0,-1,1,-1,0]
    while True:
        fast_testing(n,1000,hehe)
        print(main()) 


if __name__=="__main__":
    training(4)
