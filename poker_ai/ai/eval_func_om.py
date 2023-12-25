import math
import multiprocessing
import random
from poker_ai.poker.poker_component import Player, Hand, Deck
from poker_ai.constant import DEEPNESS,CONFIDENT_RATE,OPPONENT_CONFIDENT_RANGE,UPDATE_WEIGHT

def simulation_random_number(call_conf_dict):
    res=1
    for player_name in call_conf_dict:
        if random.random()<call_conf_dict[player_name]:
            res+=1
    return res

def multi_process_eval_func(player, num_players, board, call_conf_dict):
    """Return the winning/tie chance of a hand, using Monte-Carlo simulations. AND it's multiprocess

    Args:
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        player_1 (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    Returns:
        tuple(float,float): the winning and tie chance of the hand.
    """
    a = len(board.hand.cards)
    if a == 0:
        state = 0
    elif a == 3:
        state = 1
    elif a == 4:
        state = 2
    else:
        state = 3
    win, draw = 0, 0
    if state!=3:
        deepness=5*DEEPNESS
        with multiprocessing.Pool() as pool:
            simulation_num= pool.map(simulation_random_number, [call_conf_dict for _ in range(deepness)])
            result = pool.starmap(singly_function, [(player, simulation_num[x], board, state) for x in range(deepness)])
            for x in range(deepness):
                win += result[x][0]
                draw += result[x][1]
        return (win/deepness, draw/deepness)
    else:
        with multiprocessing.Pool() as pool:
            result = pool.starmap(singly_function, [(player, num_players, board, state) for _ in range(DEEPNESS)])
            for x in range(DEEPNESS):
                win += result[x][0]
                draw += result[x][1]
        return (win/DEEPNESS, draw/DEEPNESS)

def singly_function(player, num_players, board, state):
    temp_board = Player(Hand(), "Board", 0)
    temp_board.hand.cards = board.hand.cards[:]
    deck = Deck()
    for card in player.hand.cards:
        deck.remove_card(card)
    for card in temp_board.hand.cards:
        deck.remove_card(card)
    return auto_predefined_game(num_players, player, temp_board, state, deck)

def eval_func(player, num_players, board, call_conf_dict):
    """Return the winning/tie chance of a hand, using Monte-Carlo simulations.

    Args:
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        player_1 (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    Returns:
        tuple(float,float): the winning and tie chance of the hand.
    """
    win, draw = 0, 0
    a = len(board.hand.cards)
    if a == 0:
        state = 0
    elif a == 3:
        state = 1
    elif a == 4:
        state = 2
    else:
        state=3
    if state!=3:
        a=5
        for _ in range(DEEPNESS*a):
            temp_board = Player(Hand(), "Board", 0)
            temp_board.hand.cards = board.hand.cards[:]
            deck = Deck()
            for card in player.hand.cards:
                deck.remove_card(card)
            for card in temp_board.hand.cards:
                deck.remove_card(card)
            num_sim=simulation_random_number(call_conf_dict)
            temp = auto_predefined_game(num_sim, player, temp_board, state, deck) 
            win += temp[0]
            draw += temp[1]
    else:
        a=1
        for _ in range(DEEPNESS*a):
            temp_board = Player(Hand(), "Board", 0)
            temp_board.hand.cards = board.hand.cards[:]
            deck = Deck()
            for card in player.hand.cards:
                deck.remove_card(card)
            for card in temp_board.hand.cards:
                deck.remove_card(card)
            temp = auto_predefined_game(num_players, player, temp_board, state, deck) 
            win += temp[0]
            draw += temp[1]
    return (win/(DEEPNESS*a), draw/(a*DEEPNESS))
    
def auto_predefined_game(num_players, player_1, board, turn, deck):
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
            (0,1) if win with 1 or more people (or draw in other words)
            (1,0) if win alone
    """
    if num_players == 1:
        return (1, 0)
    players = [player_1]
    hands = deck.deal_hands(num_players-1, 2)
    for x in range(num_players-1):
        players.append(Player(hands.pop(), f"Player {x+2}", 0))
    for k in range(turn, 3):
        if k == 0:
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
        elif k >= 1:
            board.hand.add_card(deck.deal_cards())
    self = players[0].hand.create_poker(board.hand).check()
    checker = []
    for player in players[1:]:
        checker.append(player.hand.create_poker(board.hand).check())
    win = max(checker)
    if win > self:
        return (0, 0)
    elif win == self:
        return (0, 1)
    else:
        return (1, 0)    
    
def create_enumerate_dict(player, board, turn):
    deck=Deck()
    for card in player.hand.cards:
        deck.remove_card(card)
    for card in board.hand.cards:
        deck.remove_card(card)
    weight_dict={}
    prob_dict={}
    deepness=DEEPNESS//333
    with multiprocessing.Pool() as pool:
        result=pool.starmap(single_solo_game,[(player, card1, card2, board, deck, turn) for card1 in range(0,50-turn) for card2 in range(card1+1,50-turn) for _ in range(deepness)])
        for hand,value in result:
            if hand in prob_dict:
                weight_dict[hand][0]+=value[0]/deepness
                weight_dict[hand][1]+=value[1]/deepness
            else:
                weight_dict[hand]=[value[0]/deepness,value[1]/deepness]
                prob_dict[hand]=2/(50*51)
    return (weight_dict,prob_dict)


def enumerate_func(player,opponent_index,gamelogger):
    turn=gamelogger.action_history[opponent_index]
    return (sum(player.weighted_dict[turn][key][0]*player.opponent_prob_dict[opponent_index][turn][key] for key in player.weighted_dict[turn]),
            sum(player.weighted_dict[turn][key][1]*player.opponent_prob_dict[opponent_index][turn][key] for key in player.weighted_dict[turn]))

def update_weighted_dict(player, board, turn, gamelogger):
    match turn:
        case 5:
            preturn=4
        case 4:
            preturn=3
        case 3:
            preturn=0
        case 0:
            return
        case _:
            raise ValueError("update_weighted_dict error")
    deck=Deck()
    for card in player.hand.cards:
        deck.remove_card(card)
    for card in board.hand.cards:
        deck.remove_card(card)
    player.weighted_dict[turn]={}
    deepness=DEEPNESS//333
    for opponent_name in player.opponent_prob_dict:
        if turn not in player.opponent_prob_dict[opponent_name]:
            player.opponent_prob_dict[opponent_name][turn]={}
            player.partition_prob_dict[opponent_name][turn]={}
    with multiprocessing.Pool() as pool:
        result=pool.starmap(single_solo_game,[(player, card1, card2, board, deck, turn) for card1 in range(0,50-turn) for card2 in range(card1+1,50-turn) for _ in range(deepness)])
        for hand,value in result:
            if value is not None:
                if hand in player.weighted_dict[turn]:
                    player.weighted_dict[turn][hand][0]+=value[0]/deepness
                    player.weighted_dict[turn][hand][1]+=value[1]/deepness
                else:
                    player.weighted_dict[turn][hand]=[value[0]/deepness,value[1]/deepness]
                for opponent_name in player.opponent_prob_dict:
                    player.opponent_prob_dict[opponent_name][turn][hand]=player.opponent_prob_dict[opponent_name][preturn][hand]
                    
def update_prob_dict(player, turn, gamelogger):
    for opponent_name,opponent_action_turn,action in gamelogger.history[::-1]:
        if opponent_name==player.name:
            return
        else:
            if player.opponent_can_act[opponent_name]:
                if opponent_action_turn==turn:     
                    if action==7:
                        player.opponent_can_act[opponent_name]=False
                        player.opponent_ingame[opponent_name]=False
                        continue
                    elif action==8:
                        player.opponent_can_act[opponent_name]=False
                        bot_ratio,top_ratio=OPPONENT_CONFIDENT_RANGE[action]
                    else:
                        bot_ratio,top_ratio=OPPONENT_CONFIDENT_RANGE[action]
                    temp_dict=[(key,item) for key,item in player.weighted_dict[turn].items()]
                    temp_dict.sort(key=lambda a: a[1][0]+a[1][1],reverse=True)
                    len_dict=len(temp_dict)
                    bot,top=int(abs(bot_ratio)*len_dict),int((1-abs(top_ratio))*len_dict)
                    if top_ratio<0 and bot_ratio<0:  
                        total_reduced_prob=0
                        for k in range(0,bot):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        for k in range(top,len_dict):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/(bot+(len_dict-top))
                        for k in range(bot,top):
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]+=prob_increment
                    elif top_ratio>0:
                        total_reduced_prob=0
                        for k in range(0,bot):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/bot
                        for k in range(top,len_dict):
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]+=prob_increment
                    elif bot_ratio>0:
                        total_reduced_prob=0
                        for k in range(top,len_dict):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/(len_dict-top)
                        for k in range(0,bot):
                            player.opponent_prob_dict[opponent_name][turn][temp_dict[k][0]]+=prob_increment
                    
                    total=1/sum(player.opponent_prob_dict[opponent_name][turn].values())
                    if total!=1:
                        for key in player.opponent_prob_dict[opponent_name][turn]:
                            player.opponent_prob_dict[opponent_name][turn][key]*=total
                    a=10
                    for partition in range(a):
                        bot=int(len_dict*partition*0.1)
                        top=int(len_dict*(partition+1)*0.1)
                        total_prob=0
                        for item in temp_dict[bot:top]:
                            total_prob+=player.opponent_prob_dict[opponent_name][turn][item[0]]
                        player.partition_prob_dict[opponent_name][turn][partition+1]=total_prob
                else:
                    match turn:
                        case 5:
                            temp_turn=4
                        case 4:
                            temp_turn=3
                        case 3:
                            temp_turn=0
                        case _:
                            raise ValueError("The turn value in update_prob_dict is wrong")
                    if action==7:
                        player.opponent_can_act[opponent_name]=False
                        continue
                    elif action==8:
                        player.opponent_can_act[opponent_name]=False
                        bot_ratio,top_ratio=OPPONENT_CONFIDENT_RANGE[action]
                    else:
                        bot_ratio,top_ratio=OPPONENT_CONFIDENT_RANGE[action]
                    temp_dict=[(key,item) for key,item in player.weighted_dict[temp_turn].items()]
                    temp_dict.sort(key=lambda a: a[1][0]+a[1][1],reverse=True)
                    len_dict=len(temp_dict)
                    bot,top=int(abs(bot_ratio)*len_dict),int((1-abs(top_ratio))*len_dict)
                    if top_ratio<0 and bot_ratio<0:
                        total_reduced_prob=0
                        for k in range(0,bot):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        for k in range(top,len_dict):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/(bot+(len_dict-top))
                        for k in range(bot,top):
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]+=prob_increment
                    elif top_ratio>0:
                        total_reduced_prob=0
                        for k in range(0,bot):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/bot
                        for k in range(top,len_dict):
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]+=prob_increment
                    elif bot_ratio>0:        
                        total_reduced_prob=0
                        for k in range(top,len_dict):
                            total_reduced_prob+=player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*(1-UPDATE_WEIGHT)
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]*=UPDATE_WEIGHT
                        prob_increment=total_reduced_prob/(len_dict-top)
                        for k in range(0,bot):
                            player.opponent_prob_dict[opponent_name][temp_turn][temp_dict[k][0]]+=prob_increment
                    
                    total=1/sum(player.opponent_prob_dict[opponent_name][temp_turn].values())
                    if total!=1:
                        for key in player.opponent_prob_dict[opponent_name][temp_turn]:
                            player.opponent_prob_dict[opponent_name][temp_turn][key]*=total
                    a=10
                    for partition in range(a):
                        bot=int(len_dict*partition*0.1)
                        top=int(len_dict*(partition+1)*0.1)
                        total_prob=0
                        for item in temp_dict[bot:top]:
                            total_prob+=player.opponent_prob_dict[opponent_name][temp_turn][item[0]]
                        player.partition_prob_dict[opponent_name][temp_turn][partition+1]=total_prob
        

def single_solo_game(player, card1, card2, board, deck, turn):
    card_1=deck.cards[card1]
    card_2=deck.cards[card2]
    temp_deck=Deck()
    temp_deck.cards=deck.cards[:]
    temp_deck.remove_card(card_1)
    temp_deck.remove_card(card_2)
    opponent_hand=Hand()
    opponent_hand.add_card(card_1)
    opponent_hand.add_card(card_2)
    opponent_hand.cards.sort()
    hand_str=opponent_hand.printhandsimple()
    for card in board.hand.cards:
        if card==card_1 or card==card_2:
            return (hand_str,None)
    temp_board=Player(Hand(),"",0)
    temp_board.hand.cards=board.hand.cards[:]
    temp_deck.shuffle()
    for _ in range(turn,5):
        temp_board.hand.add_card(temp_deck.deal_cards())
    self = player.hand.create_poker(temp_board.hand).check()
    other = opponent_hand.create_poker(temp_board.hand).check()
    if self>other:
        return (hand_str,(1,0))
    if self==other:
        return (hand_str,(0,1))
    return (hand_str,(0,0))
