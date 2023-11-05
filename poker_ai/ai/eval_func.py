import math
import multiprocessing
from poker_ai.poker.poker_component import Player,Hand,Deck

###################################
#Constant

DEEPNESS=40000
# The number of iterations of the Monte-Carlo simulation. Higher is better but requires more time and memory
# Recommended deepness: 10000 for single or test, 40000 for multi and playing
CONFIDENT_RATE=0.8
# The base confident_rate of a player, represent the chance that the player will check/call in a 2 player games
# Don't ask where I get this number, it's taken by testing a lot

###################################

def multi_process_eval_func(player, num_players, board):
    """Return the winning/tie chance of a hand, using Monte-Carlo simulations and simple Bayes belief network. AND it's multiprocess

    Args:
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        player_1 (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    Returns:
        tuple(float,float): the winning and tie chance of the hand.
    """
    CALL_CONFIDENT=CONFIDENT_RATE**math.log(num_players-1,1.5)
    # I tried many functions for the call_confident, and this is the best I can get. I don't know but simply ln(num_players-1) doesn't work
    a=len(board.hand.cards)
    if a==0:
        state=0
    elif a==3:
        state=1
    elif a==4:
        state=2
    else:
        state=3
    win,draw=0,0
    with multiprocessing.Pool() as pool:
        for k in range(num_players):
            tempwin=0
            tempdraw=0
            result=pool.starmap(singly_function,[(player,num_players-k,board,state) for _ in range(DEEPNESS)])
            for x in range(DEEPNESS):
                tempwin+=result[x][0]
                tempdraw+=result[x][1]
            win+=tempwin*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
            draw+=tempdraw*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
    return (win/DEEPNESS,draw/DEEPNESS)

def singly_function(player, num_players, board, state):
    temp_board=Player(Hand(),"Board",0)
    temp_board.hand.cards=board.hand.cards[:]
    deck=Deck()
    for card in player.hand.cards:
        deck.remove_card(card)
    for card in temp_board.hand.cards:
        deck.remove_card(card)
    return auto_predefined_game(num_players,player,temp_board,state,deck)

def eval_func(player, num_players, board):
    """Return the winning/tie chance of a hand, using Monte-Carlo simulations and simple Bayes belief network.

    Args:
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        player_1 (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    Returns:
        tuple(float,float): the winning and tie chance of the hand.
    """
    CALL_CONFIDENT=CONFIDENT_RATE**math.log(num_players-1,1.5)
    # I tried many functions for the call_confident, and this is the best I can get. I don't know but simply ln(num_players-1) doesn't work
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
    for k in range(0,num_players):
        tempwin=0
        tempdraw=0
        for _ in range(DEEPNESS):
            temp_board=Player(Hand(),"Board",0)
            temp_board.hand.cards=board.hand.cards[:]
            deck=Deck()
            for card in player.hand.cards:
                deck.remove_card(card)
            for card in temp_board.hand.cards:
                deck.remove_card(card)
            temp=auto_predefined_game(num_players-k,player,temp_board,state,deck) 
            tempwin+=temp[0]
            tempdraw+=temp[1]
        #Just some simple Bayes's theorem, Mr Do Van Cuong will disappoint at you if you don't know what this is       
        #Ok, let A: player 1 win. B(k): there are num_player-1-k player other than you are playing, means that k player are out/folded
        #C: player x not fold. P(C) is the CALL_CONFIDENT
        #Bayes's theorem: P(B(k))=comb(num_players-1,k)*(P(C)^(num_players-1-k))*((1-P(C))^k)
        #If we let P(C)=1, then it's simply all in game. In a 2-player game, the chances are pretty balanced, and we always should use that case.
        #But in a multiplayer game, for ex: 5-6 players, the chances get super low. For example, the winning chances of a pair As hand is lower than 50%.
        #But of course, in reality, player with pair As will just raise high so that others player will fold.
        #The choice 0.8 is gotten by testing a lot. Don't ask why i get that number 
        #Bayes's theorem: P(A)=sum of all P(A|B(K))*P(B(k))
        #P(A|B(k))=tempwin
        win+=tempwin*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
        draw+=tempdraw*(CALL_CONFIDENT**(num_players-1-k))*((1-CALL_CONFIDENT)**k)*math.comb(num_players-1,k)
        
    return (win/DEEPNESS,draw/DEEPNESS)


def auto_predefined_game(num_players,player_1,board,turn,deck):
    """Return the result of a auto game, where the AI cards and some(or none/all) of the community cards are dealt, and all the others
        player's cards are unknown. The other's card and the leftover community cards will be randomized.

    Args:
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        player_1 (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
        turn (int): the current phase of the round:
            0: Preflop, 0 community card 
            1: Flop, 3 community card
            2: Turn, 4 community card
            3: River, 5 community card
        deck (poker_ai.poker.poker_component.Deck()): the deck of the current game. Of course, the deck will consist of all 52 cards,
            exclude the cards that are dealt to the player_1 and board 

    Returns:
        tuple: the win/tie tuple of the game. It should return:
            (0,0) if loss
            (0,1) if win with 1 or more people
            (1,0) if win alone
    """
    if num_players==1:
        return (1,0)
    players=[player_1]
    hands=deck.deal_hands(num_players-1,2)
    for x in range(num_players-1):
        players.append(Player(hands.pop(),f"Player {x+2}",0))
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