from poker_ai.ai.eval_func import enumerate_func,create_enumerate_dict,eval_func
from poker_ai.poker.poker_component import Hand,Card,Player

def main():
    for card1 in range(1,14):
        for card2 in range(1,14):
            if card1>card2:
                a=Player(Hand(),"0",0)
                board=Player(Hand(),"0",0)
                a.hand.add_card(Card(card1,1))
                a.hand.add_card(Card(card2,1))
                hehe=a.hand.printhandsimple()
                # board.hand.add_card(Card(10,2))
                # board.hand.add_card(Card(3,1))
                # board.hand.add_card(Card(2,3))
                x,y=create_enumerate_dict(a,board,0)
                a.weighted_dict[1],a.opponent_prob_dict[1]=x.copy(),y.copy()
                print(hehe,eval_func(a,6,board))
            else:
                a=Player(Hand(),"0",0)
                board=Player(Hand(),"0",0)
                a.hand.add_card(Card(card1,1))
                a.hand.add_card(Card(card2,2))
                hehe=a.hand.printhandsimple()
                # board.hand.add_card(Card(10,2))
                # board.hand.add_card(Card(3,1))
                # board.hand.add_card(Card(2,3))
                x,y=create_enumerate_dict(a,board,0)
                a.weighted_dict[1],a.opponent_prob_dict[1]=x.copy(),y.copy()
                print(hehe,eval_func(a,6,board))
if __name__=="__main__":
    main()