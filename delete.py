from poker_ai.ai.eval_func import eval_func
from poker_ai.poker.poker_component import Hand,Player,Card

a=Player(Hand(),"0",0)
board=Player(Hand(),"0",0)
a.hand.add_card(Card(13,0))
a.hand.add_card(Card(11,1))
board.hand.add_card(Card(10,2))
board.hand.add_card(Card(3,1))
board.hand.add_card(Card(2,3))
print(eval_func(a,2,board))