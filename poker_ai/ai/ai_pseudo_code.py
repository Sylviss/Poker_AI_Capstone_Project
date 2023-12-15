import math
import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func, create_enumerate_dict, enumerate_func, update_prob_dict, update_weighted_dict
from poker_ai.constant import CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN,CALL_RANGE,BLUFF_RANGE, RULE_DICT, BETTED_DICT
from poker_ai.poker.poker_component import Player,Deck
from copy import deepcopy
class MCTS_Node:
    def __init__(self, player_name, turn, parent=None):
        """For the actions initialization:
            0: Fold
            1: Check/call
            2: Raise/All in/Raise max/Raise something blah blah
            Also, for the sake of simulation and less branch, the AI will only attempt to raise for 4 times. The 4th time will always be raise max/all in
            For the turn initialization:
            -1: End state
            0: Pre-flop
            1: Flop
            2: Turn
            3: River
        """
        self.player_name = player_name
        self.turn = turn
        self.visits = 0
        self.values = 0
        self.children = {}
        self.parent = parent
        
def selection(root, cur_iteration):
    if cur_iteration<1000:
        if len(root.children)==0:
            return root
        else:
            choices=root.children.keys()
            next_node=random.choice(choices)
            return selection(root.children[next_node],cur_iteration)
    else:
        if len(root.children)==0:
            return root
        else:
            ev_list=expected_value_gen(root)
            next_node=max(ev_list,key=lambda a:a[1])[0]
            return selection(root.children[next_node],cur_iteration)

def expected_value_gen(root):
    res=[]
    for key,node in root.children.items():
        ev=node.values/node.visits + UBC1_CONSTANT*(math.log(node.parent.visits)/node.visits)**0.5
        res.append([key,ev])
    return res

def expansion(root,actions,next_turn,next_player_name):
    if root.turn!=-1:
        for action in actions:
            root.children[action]=MCTS_Node(next_player_name,next_turn,root)
            
def simulation(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp):
    return (simulation_self(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp),
        simulation_other(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp))

def simulation_self(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp):
    player_1=players_temp[index]
    gamelogger=gamelogger_temp.deepcopy()
    preflop_small_blind_value=preflop_big_blind_value//2
    num_players=len(players_temp)
    playing = num_players
    players = []
    for x in range(num_players):
        if x!=index:
            players.append(Player(None, players_temp[x].name, players_temp[x].money + players_temp[x].pot))
        else:
            cur_player=player_1.deepcopy()
            cur_player.money=player_1[x].money + player_1[x].pot
            cur_player.state = -1
            players.append(cur_player)
        if players_temp[x].state==6:
            players[x].state=6
            playing-=1
    deck = Deck()
    hands = deck.deal_hands(playing - 1, 2)
    board = board_temp.deepcopy()
    for x in range(num_players):
        players[x].pot = 0
        if players[x].state != 6 and x!=index:
            players[x].hand = hands.pop()
            players[x].state = -1
    folded = 0
    for k in range(4):
        if k != 0:
            last_raised, cur_raise = None, preflop_big_blind_value
            for player in players:
                if player.state not in [0, 3, 4, 5, 6]:
                    player.state = -1
        if k == 0:
            if players[big_blind].money <= preflop_big_blind_value:
                players[big_blind].pot = players[big_blind].money
                players[big_blind].money = 0
                players[big_blind].state = 0
                cur_call, last_raised, cur_raise = players[big_blind].pot, None, players[big_blind].pot
                board.money += players[big_blind].pot
            else:
                players[big_blind].money -= preflop_big_blind_value
                players[big_blind].pot = preflop_big_blind_value
                cur_call, last_raised, cur_raise = preflop_big_blind_value, None, preflop_big_blind_value
                board.money += preflop_big_blind_value
            if players[small_blind].money <= preflop_small_blind_value:
                players[small_blind].pot = players[small_blind].money
                players[small_blind].money = 0
                players[small_blind].state = 0
                board.money += players[small_blind].pot
            else:
                players[small_blind].money -= preflop_small_blind_value
                players[small_blind].pot = preflop_small_blind_value
                board.money += preflop_small_blind_value
            if players[big_blind].pot < players[small_blind].pot:
                cur_call, last_raised, cur_raise = preflop_small_blind_value, None, preflop_small_blind_value
        if k >= 2 and len(board.hand.cards)<2+k:
            board.hand.add_card(deck.deal_cards())
        elif k == 1 and len(board.hand.cards)==0:
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
        conditioner = True
        index = (big_blind+1) % num_players
        match = 0
        while conditioner:
            if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                conditioner = False
                break
            if players[index].state in [-1, 1, 2]:
                cur_call, last_raised, board.money, cur_raise = action_simulation(index, players, cur_call, last_raised, cur_raise, board, gamelogger)
            if players[index].state == 4:
                players[index].state = 5
                folded += 1
                if folded >= playing-1:
                    conditioner = False
                    break
            if players[index].state != 6:
                match += 1
            if (match == playing and last_raised is None):
                conditioner = False
                break
            index = (index+1) % num_players
        if folded == playing-1:
            break
    if folded == playing-1:
        if cur_player.state not in [3,4,5,6]:
            cur_player.money+=board.money
        return (cur_player.money-player_1[x].money+player_1[x].pot)/preflop_big_blind_value
    checker = []
    for player in players:
        if player.state in [0, 1, 2]:
            checker.append(player.hand.create_poker(board.hand).check())
        else:
            checker.append((0, 0))
    win = max(checker)
    winner = []
    for checker_items in checker:
        if checker_items == win:
            winner.append(1)
        else:
            winner.append(0)
    money_win = board.money//sum(winner)
    if cur_player.state not in [3,4,5,6]:
        cur_player.money+=money_win
    return (cur_player.money-player_1[x].money+player_1[x].pot)/preflop_big_blind_value
    
def action_simulation(index, players, cur_call, last_raised, cur_raise, board, gamelogger):
    turn_dict={0:0,3:1,4:2,5:3}
    action_dict={1:2,2:3,3:3,4:4,5:4,6:4,7:5,8:1}
    cur_turn=turn_dict[len(board.hand.cards)]
    if len(gamelogger.history)!=0:
        player_name,turn,action=gamelogger.history.pop(0)
        if turn!=cur_turn or player_name!=players[index].name:
            raise ValueError("action_simulation error")
        a=action_dict[action]
        if a in (3,6):
            money=gamelogger.raise_history.pop(0)[2]
        ans = 0
        self=players[index]
        if a == 1:
            if self.money <= cur_call-self.pot:
                ans = self.all_in_1(cur_call, last_raised, board.money, cur_raise)
            else:
                ans = self.all_in_2(cur_call, last_raised, board.money, cur_raise)
        elif a == 2:
            gamelogger.keylogging(self,[2])
            ans = self.check(cur_call, last_raised, board.money, cur_raise)
        elif a == 3:
            ans = self.call(cur_call, last_raised, board.money, cur_raise)
        elif a == 4:
            ans = self.raise_money(money, cur_call, last_raised, board.money, cur_raise)
        elif a == 5:
            ans = self.fold(cur_call, last_raised, board.money, cur_raise)
        return ans
    else:
        self=players[index]
        if (cur_call > self.pot and self.money > cur_call-self.pot):
            ans = self.call(cur_call, last_raised, board.money, cur_raise)
        elif cur_call==self.pot:
            ans = self.check(cur_call, last_raised, board.money, cur_raise)
        else:
            ans = self.fold(cur_call, last_raised, board.money, cur_raise)
        return ans
            
def simulation_other(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp):
    player_1=players_temp[index]
    gamelogger=gamelogger_temp.deepcopy()
    preflop_small_blind_value=preflop_big_blind_value//2
    num_players=len(players_temp)
    playing = num_players
    players = []
    for x in range(num_players):
        if x!=index:
            players.append(Player(None, players_temp[x].name, players_temp[x].money + players_temp[x].pot))
        else:
            cur_player=Player(None, players_temp[x].name, players_temp[x].money + players_temp[x].pot)
            players.append(cur_player)
        if players_temp[x].state==6:
            players[x].state=6
            playing-=1
    deck = Deck()
    hands = deck.deal_hands(playing , 2)
    board = board_temp.deepcopy()
    for x in range(num_players):
        players[x].pot = 0
        if players[x].state != 6:
            players[x].hand = hands.pop()
            players[x].state = -1
    folded = 0
    for k in range(4):
        if k != 0:
            last_raised, cur_raise = None, preflop_big_blind_value
            for player in players:
                if player.state not in [0, 3, 4, 5, 6]:
                    player.state = -1
        if k == 0:
            if players[big_blind].money <= preflop_big_blind_value:
                players[big_blind].pot = players[big_blind].money
                players[big_blind].money = 0
                players[big_blind].state = 0
                cur_call, last_raised, cur_raise = players[big_blind].pot, None, players[big_blind].pot
                board.money += players[big_blind].pot
            else:
                players[big_blind].money -= preflop_big_blind_value
                players[big_blind].pot = preflop_big_blind_value
                cur_call, last_raised, cur_raise = preflop_big_blind_value, None, preflop_big_blind_value
                board.money += preflop_big_blind_value
            if players[small_blind].money <= preflop_small_blind_value:
                players[small_blind].pot = players[small_blind].money
                players[small_blind].money = 0
                players[small_blind].state = 0
                board.money += players[small_blind].pot
            else:
                players[small_blind].money -= preflop_small_blind_value
                players[small_blind].pot = preflop_small_blind_value
                board.money += preflop_small_blind_value
            if players[big_blind].pot < players[small_blind].pot:
                cur_call, last_raised, cur_raise = preflop_small_blind_value, None, preflop_small_blind_value
        if k >= 2 and len(board.hand.cards)<2+k:
            board.hand.add_card(deck.deal_cards())
        elif k == 1 and len(board.hand.cards)==0:
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
        conditioner = True
        index = (big_blind+1) % num_players
        match = 0
        while conditioner:
            if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                conditioner = False
                break
            if players[index].state in [-1, 1, 2]:
                cur_call, last_raised, board.money, cur_raise = action_simulation(index, players, cur_call, last_raised, cur_raise, board, gamelogger)
            if players[index].state == 4:
                players[index].state = 5
                folded += 1
                if folded >= playing-1:
                    conditioner = False
                    break
            if players[index].state != 6:
                match += 1
            if (match == playing and last_raised is None):
                conditioner = False
                break
            index = (index+1) % num_players
        if folded == playing-1:
            break
    if folded == playing-1:
        if cur_player.state not in [3,4,5,6]:
            cur_player.money+=board.money
        return (cur_player.money-player_1[x].money+player_1[x].pot)/preflop_big_blind_value
    checker = []
    for player in players:
        if player.state in [0, 1, 2]:
            checker.append(player.hand.create_poker(board.hand).check())
        else:
            checker.append((0, 0))
    win = max(checker)
    winner = []
    for checker_items in checker:
        if checker_items == win:
            winner.append(1)
        else:
            winner.append(0)
    money_win = board.money//sum(winner)
    if cur_player.state not in [3,4,5,6]:
        cur_player.money+=money_win
    return (cur_player.money-player_1[x].money+player_1[x].pot)/preflop_big_blind_value       

def create_tree(player, gamelogger, big_blind_name):
    head=MCTS_Node(big_blind_name,0,None)
    action_dict={}
    cur_node=head
    for turn in gamelogger.history:
        for player_name,action in turn:
            cur_node.player_name=player_name
            cur_node.children[action_dict[action]]=MCTS_Node(None,0,cur_node)
            cur_node=cur_node.children[action_dict[action]]
    cur_node.player_name=player.name
    return (head,cur_node)

def update_tree(player_1,gamelogger):
    cur_node=player_1.root_node_tree
    action_dict={}
    for turn in gamelogger.history:
        for player,action in turn:
            if player!=cur_node.player_name:
                if cur_node.player_name is None:
                    cur_node.player_name=player
                else:
                    raise ValueError("update_tree error")
            if action_dict[action] in cur_node.children:
                cur_node=cur_node.children[action_dict[action]]
            else:
                cur_node.children[action_dict[action]]=MCTS_Node(None,0,cur_node)
                cur_node=cur_node.children[action_dict[action]]
    if cur_node.player_name is None:
        cur_node.player_name=player_1.name
    return cur_node
            

def next_parameter(index, players_temp, big_blind, small_blind, preflop_big_blind_value, board_temp, gamelogger_temp):
    player_1=players_temp[index]
    gamelogger=gamelogger_temp.deepcopy()
    preflop_small_blind_value=preflop_big_blind_value//2
    num_players=len(players_temp)
    playing = num_players
    players = []
    for x in range(num_players):
        if x!=index:
            players.append(Player(None, players_temp[x].name, players_temp[x].money + players_temp[x].pot))
        else:
            cur_player=player_1.deepcopy()
            cur_player.money=player_1[x].money + player_1[x].pot
            cur_player.state = -1
            players.append(cur_player)
        if players_temp[x].state==6:
            players[x].state=6
            playing-=1
    deck = Deck()
    hands = deck.deal_hands(playing - 1, 2)
    board = board_temp.deepcopy()
    for x in range(num_players):
        players[x].pot = 0
        if players[x].state != 6 and x!=index:
            players[x].hand = hands.pop()
            players[x].state = -1
    folded = 0
    for k in range(4):
        if k != 0:
            last_raised, cur_raise = None, preflop_big_blind_value
            for player in players:
                if player.state not in [0, 3, 4, 5, 6]:
                    player.state = -1
        if k == 0:
            if players[big_blind].money <= preflop_big_blind_value:
                players[big_blind].pot = players[big_blind].money
                players[big_blind].money = 0
                players[big_blind].state = 0
                cur_call, last_raised, cur_raise = players[big_blind].pot, None, players[big_blind].pot
                board.money += players[big_blind].pot
            else:
                players[big_blind].money -= preflop_big_blind_value
                players[big_blind].pot = preflop_big_blind_value
                cur_call, last_raised, cur_raise = preflop_big_blind_value, None, preflop_big_blind_value
                board.money += preflop_big_blind_value
            if players[small_blind].money <= preflop_small_blind_value:
                players[small_blind].pot = players[small_blind].money
                players[small_blind].money = 0
                players[small_blind].state = 0
                board.money += players[small_blind].pot
            else:
                players[small_blind].money -= preflop_small_blind_value
                players[small_blind].pot = preflop_small_blind_value
                board.money += preflop_small_blind_value
            if players[big_blind].pot < players[small_blind].pot:
                cur_call, last_raised, cur_raise = preflop_small_blind_value, None, preflop_small_blind_value
        if k >= 2 and len(board.hand.cards)<2+k:
            board.hand.add_card(deck.deal_cards())
        elif k == 1 and len(board.hand.cards)==0:
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
            board.hand.add_card(deck.deal_cards())
        conditioner = True
        index = (big_blind+1) % num_players
        match = 0
        while conditioner:
            if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                conditioner = False
                break
            if players[index].state in [-1, 1, 2]:
                cur_call, last_raised, board.money, cur_raise = action_taker(index, players, cur_call, last_raised, cur_raise, board, gamelogger)
            if cur_call==None:
                return (last_raised, board.money, cur_raise)
            if players[index].state == 4:
                players[index].state = 5
                folded += 1
                if folded >= playing-1:
                    conditioner = False
                    break
            if players[index].state != 6:
                match += 1
            if (match == playing and last_raised is None):
                conditioner = False
                break
            index = (index+1) % num_players
        if folded == playing-1:
            break
    return ([],-1,"Terminal Node")
    
def action_taker(index, players, cur_call, last_raised, cur_raise, board, gamelogger):
    turn_dict={0:0,3:1,4:2,5:3}
    action_dict={1:2,2:3,3:3,4:4,5:4,6:4,7:5,8:1}
    cur_turn=turn_dict[len(board.hand.cards)]
    if len(gamelogger.history)!=0:
        player_name,turn,action=gamelogger.history.pop(0)
        if turn!=cur_turn or player_name!=players[index].name:
            raise ValueError("action_simulation error")
        a=action_dict[action]
        if a in (3,6):
            money=gamelogger.raise_history.pop(0)[2]
        ans = 0
        self=players[index]
        if a == 1:
            if self.money <= cur_call-self.pot:
                ans = self.all_in_1(cur_call, last_raised, board.money, cur_raise)
            else:
                ans = self.all_in_2(cur_call, last_raised, board.money, cur_raise)
        elif a == 2:
            gamelogger.keylogging(self,[2])
            ans = self.check(cur_call, last_raised, board.money, cur_raise)
        elif a == 3:
            ans = self.call(cur_call, last_raised, board.money, cur_raise)
        elif a == 4:
            ans = self.raise_money(money, cur_call, last_raised, board.money, cur_raise)
        elif a == 5:
            ans = self.fold(cur_call, last_raised, board.money, cur_raise)
        return ans
    else:
        self=players[index]
        min_money=min([(player.money+player.pot)-cur_call if player.state not in [4,5,6] and (player.money+player.pot)-cur_call>0 else 0 if player.state not in [4,5,6] else 2**31-1 for player in players])
        checkout = [1,5]
        if min_money!=0 and (self.money+self.pot)-cur_call>min_money:
            checkout.append(6)
        if cur_call == self.pot:
            checkout.append(2)
        elif cur_call > self.pot and self.money > cur_call-self.pot:
            checkout.append(3)
        if gamelogger.raised_time<3:
            if min_money!=0 and (self.money+self.pot)-cur_call>min_money:
                checkout.append(6)
            if self.money > cur_call-self.pot+cur_raise:
                checkout.append(4)
        elif gamelogger.raised_time==3:
            if min_money!=0 and (self.money+self.pot)-cur_call>min_money:
                checkout.append(6)
            if self.money > cur_call-self.pot+cur_raise and 6 not in checkout:
                checkout.append(4)
        return (None,checkout,len(board.hand.cards),self.name)

def backpropagation(root,reward):
    if root.parent is not None:
        root.values+=reward
        root.visits+=1
        backpropagation(root.parent,reward)
    else:
        root.values+=reward
        root.visits+=1

def choose_action(cur_node):
    return max([cur_node.children[action] for action in cur_node.children],key=lambda a: a.values/a.visits)

def mcts_ai_agent(index, players, min_money, board, actions, cur_call, cur_raise, big_blind, last_raised, gamelogger, small_blind, preflop_big_blind_value):
    big_blind_name=players[big_blind].name
    player=players[index]
    turn_dict={0:0,3:1,4:2,5:3}
    turn = turn_dict[len(board.hand.cards)]
    if turn==0:
        player.root_node_tree,player.mcts_tree=create_tree(player, gamelogger, big_blind_name)
    else:
        player.mcts_tree=update_tree(player,gamelogger)
    cur_node=player.mcts_tree
    for k in range(1000):
        selected_node=selection(cur_node,k)
        actions,next_turn,next_player_name=next_parameter(index, players, big_blind, small_blind, preflop_big_blind_value, board, gamelogger)
        expansion(selected_node,actions,next_turn,next_player_name)
        reward=simulation(index, players, big_blind, small_blind, preflop_big_blind_value, board, gamelogger)
        backpropagation(cur_node,reward)
    actions=choose_action(cur_node)
    return [actions]