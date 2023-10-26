import math
from poker_ai.poker.poker_component import Player,Hand,Deck,Card
###################################
#Constant

DEEPNESS=10000
E_NUMBER=2.71828
CONFIDENT_RATE=0.8

###################################
def eval_func(player, num_players: int, board) -> float:
    CALL_CONFIDENT=CONFIDENT_RATE**math.log(num_players-1,1.5)
    win,draw=0,0
    a=len(board.hand.cards)
    if a==0:
        state=0
    elif a==3:
        state=1
    elif a==4:
        state=2
    else:
        state=3
    for _ in range(DEEPNESS):
        tempwin=0
        tempdraw=0
        for k in range(0,num_players):
            temp_board=Player(Hand(),"Board",0)
            temp_board.hand.cards=board.hand.cards[:]
            deck=Deck()
            for card in player.hand.cards:
                deck.remove_card(card)
            for card in temp_board.hand.cards:
                deck.remove_card(card)
            temp=auto_predefined_game(num_players-k,player,temp_board,state,deck)
            tempwin+=temp[0]*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
            tempdraw+=temp[1]*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
        win+=tempwin
        draw+=tempdraw
    return (win/DEEPNESS,draw/DEEPNESS)


def auto_predefined_game(num_players,player_1,board,turn,deck):
    if num_players==1:
        return (1,0)
    players=[player_1]
    hands=deck.deal_hands(num_players-1,2)
    for x in range(num_players-1):
        players.append(Player(hands.pop(),f"Player {x+1}",0))
    for k in range(turn,3):
        if k==0:
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
        elif k>=1:
            board.hand.add_card(deck.deal_cards())
    self=players[0].hand.create_poker(board.hand).check()
    checker=[]
    for player in players[1:]:
        checker.append(player.hand.create_poker(board.hand).check())
    win=max(checker)
    if win>self:
        return (0,0)
    elif win==self:
        return (0,1)
    else:
        return (1,0)