import json
from poker_ai.ai.eval_func import eval_func
from poker_ai.poker.poker_component import Player, Hand, Card

hehehe = []
for a in range(1, 14):
    for b in range(1, 14):
        print(a, b)
        if a <= b:
            x = Player(Hand(), "hehe", 0)
            x.hand.add_card(Card(a, 0))
            x.hand.add_card(Card(b, 1))
            board = Player(Hand(), "hehe", 0)
            hehehe.append((f"{x.hand.printhandsimple()}", eval_func(x, 6, board)[0]))
        else:
            x = Player(Hand(), "hehe", 0)
            x.hand.add_card(Card(a, 0))
            x.hand.add_card(Card(b, 0))
            board = Player(Hand(), "hehe", 0)
            hehehe.append((f"{x.hand.printhandsimple()}", eval_func(x, 6, board)[0]))

def wtf(a):
    """
    This function does something.
    """
    return a[1]

hehehe.sort(key=wtf)
file_path = r"D:\Repo\Poker_AI_Capstone_Project\statistic\statistic6.txt"
with open(file_path, mode="w+",encoding="utf-8") as file:
    json.dump(hehehe, file)
