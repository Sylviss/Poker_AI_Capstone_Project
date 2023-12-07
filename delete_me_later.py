import numpy as np
import matplotlib.pyplot as plt
from poker_ai.ai.eval_func import eval_func
from poker_ai.poker.poker_component import *
hehehe=[]
for a in range(1,14):
    for b in range(1,14):
        print(a,b)
        if a<=b:
            x=Player(Hand(),"hehe",0)
            x.hand.add_card(Card(a,0))
            x.hand.add_card(Card(b,1))
            board=Player(Hand(),"hehe",0)
            hehehe.append(eval_func(x,4,board)[0])
        else:
            x=Player(Hand(),"hehe",0)
            x.hand.add_card(Card(a,0))
            x.hand.add_card(Card(b,0))
            board=Player(Hand(),"hehe",0)
            hehehe.append(eval_func(x,4,board)[0])
hehehe.sort()
plt.plot(hehehe,range(1,170),'ro')
plt.show()