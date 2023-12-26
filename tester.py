from collections import defaultdict
from poker_ai.poker.play import fast_testing, game_loop_model_test
import sys,os

# Disable print
def blockPrint():
    sys.stdout = open(os.devnull, 'w', encoding="utf-8")

# Restore print
def enablePrint():
    sys.stdout = sys.__stdout__
        
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

def training_all():
    while True:
        fast_testing(2, 1000, [1,-1])
        fast_testing(2, 1000, [1,-1])
        fast_testing(2, 1000, [1,-1])
        fast_testing(3, 1000, [1,-1,1])
        fast_testing(4, 1000, [1,0,-1,-1])
        fast_testing(4, 1000, [1,0,-1,-1])
        fast_testing(5, 1000, [1,0,-1,1,-1])
        fast_testing(6, 1000, [1,0,-1,1,-1,0])

if __name__=="__main__":
    game_loop_model_test(2,1000,20,[3,6])
