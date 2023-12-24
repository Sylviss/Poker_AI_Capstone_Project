from poker_ai.poker.poker_component import Deck, Player, Hand
from poker_ai.ai.ml.methods import multi_process_eval_func_but_in_opponent_modelling

hands = Deck().cards
hand = []
for i in range(len(hands)):
    for j in range(i+1,len(hands)):
        hand.append([hands[i],hands[j]])
d = {}
tmp = Player(Hand(), 'bruh', 100)
board = Player(Hand(), 'b', 100)
for i in hand:
    tmp.hand.cards = i
    for o in i:
        board.hand.remove_card(o)
    win = multi_process_eval_func_but_in_opponent_modelling(tmp, 2, board)
