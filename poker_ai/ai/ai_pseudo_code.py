import math
import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func, create_enumerate_dict, enumerate_func, update_prob_dict, update_weighted_dict
from poker_ai.constant import CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN,CALL_RANGE,BLUFF_RANGE, RULE_DICT, BETTED_DICT

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
        ev_list=expected_value_gen(root)
        return max(ev_list,key = lambda a: a[1])

def expected_value_gen(root):
    if len(root.children.items())==0:
        ev=root.values/root.visit + UBC1_CONSTANT*(2*(math.log(root.parent.visits)/root.visits))**0.5
        return [(root,ev)]
    else:
        res=[]
        for node in root.children.items():
            res+=expected_value_gen(node)
        return res

def expansion(root,actions,next_turn,next_player_name):
    if root.turn!=-1:
        for action in actions:
            root.children[action]=MCTS_Node(next_player_name,next_turn,root)
            

def simulation(selected_node, player_1, num_players, init_money, big_blind, small_blind, preflop_big_blind_value):
    """Play a game with {num_players} player with {init_money} base money

    Args:
        num_players (int): the number of players
        init_money (int): the number of base money
    """    """"""
    indicator = 2
    playing = num_players
    players = [player_1]
    temp_board_money = 0
    for x in range(num_players-1):
        players.append(Player(None, f"Player {x+1}", init_money))
    deck = Deck()
    hands = deck.deal_hands(playing, 2)
    board = Player(Hand(), "Board", temp_board_money)
    for x in range(num_players):
        players[x].pot = 0
        if players[x].state != 6:
            players[x].hand = hands.pop()
            players[x].state = -1
    print_blind_board(players, board)
    turn = ["Preflop", "Flop", "Turn", "River"]
    folded = 0
    for k in range(4):
        gamelogger.next_turn()
        if k != 0:
            last_raised, cur_raise = None, preflop_big_blind_value
            for player in players:
                if player.state not in [0, 3, 4, 5, 6]:
                    player.state = -1
        match = 0
        print(turn[k])
        if k == 0:
            if players[big_blind].money <= preflop_big_blind_value:
                players[big_blind].pot = players[big_blind].money
                players[big_blind].money = 0
                players[big_blind].state = 0
                print(
                    f"{players[big_blind].name} is big blind and put in {players[big_blind].pot}$")
                cur_call, last_raised, cur_raise = players[big_blind].pot, None, players[big_blind].pot
                board.money += players[big_blind].pot
            else:
                players[big_blind].money -= preflop_big_blind_value
                players[big_blind].pot = preflop_big_blind_value
                print(
                    f"{players[big_blind].name} is big blind and put in {preflop_big_blind_value}$")
                cur_call, last_raised, cur_raise = preflop_big_blind_value, None, preflop_big_blind_value
                board.money += preflop_big_blind_value
            if players[small_blind].money <= preflop_small_blind_value:
                players[small_blind].pot = players[small_blind].money
                players[small_blind].money = 0
                players[small_blind].state = 0
                print(
                    f"{players[small_blind].name} is small and put in {players[small_blind].pot}$")
                board.money += players[small_blind].pot
            else:
                players[small_blind].money -= preflop_small_blind_value
                players[small_blind].pot = preflop_small_blind_value
                print(
                    f"{players[small_blind].name} is small blind and put in {preflop_small_blind_value}$")
                board.money += preflop_small_blind_value
            if players[big_blind].pot < players[small_blind].pot:
                cur_call, last_raised, cur_raise = preflop_small_blind_value, None, preflop_small_blind_value
        if k >= 2:
            board.hand.add_card(a.deal_cards())
            print_blind_board(players, board)
        elif k == 1:
            board.hand.add_card(a.deal_cards())
            board.hand.add_card(a.deal_cards())
            board.hand.add_card(a.deal_cards())
            print_blind_board(players, board)
        conditioner = True
        index = (big_blind+1) % num_players
        while conditioner:
            if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                conditioner = False
                break
            if players[index].state in [-1, 1, 2]:
                cur_call, last_raised, board.money, cur_raise = action(
                    index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger)
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
        if DEBUG_MODE==1:
            print("Post-game")
            print_board(players, board)
        for player in players:
            if player.state not in [3, 4, 5, 6]:
                print(f"{player.name} win the game!")
                player.money += board.money
                board.money = 0
                break
        for player in players:
            if player.money < 0:
                raise poker_component.WTF
            if player.money == 0 and player.state != 6:
                print(f"{player.name} broke as hell!")
                player.state = 6
                playing -= 1
        count += 1
        big_blind = (big_blind+1) % num_players
        while players[big_blind].state == 6:
            big_blind = (big_blind+1) % num_players
        small_blind = (small_blind+1) % num_players
        while players[small_blind].state == 6 or big_blind == small_blind:
            small_blind = (small_blind+1) % num_players
        temp_board_money = 0
        if STOP == 0:
            print("Press any key for the next game")
            input()
        bext.clear()
    print("Post-game")
    print_board(players, board)
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
    hehe = ", ".join(
        [players[x].name for x in range(len(winner)) if winner[x]])
    money_win = board.money//sum(winner)
    temp_board_money = board.money-money_win*sum(winner)
    for x in range(len(winner)):
        if winner[x]:
            players[x].money += money_win
    print(hehe+" win the game!")
    for player in players:
        if player.money < 0:
            raise poker_component.WTF
        if player.money == 0 and player.state != 6:
            print(f"{player.name} broke as hell!")
            player.state = 6
            playing -= 1
    if playing == 1:
        table_condition = False
        break
    count += 1
    big_blind = (big_blind+1) % num_players
    while players[big_blind].state == 6:
        big_blind = (big_blind+1) % num_players
    small_blind = (small_blind+1) % num_players
    while players[small_blind].state == 6 or big_blind == small_blind:
        small_blind = (small_blind+1) % num_players
    if STOP == 0:
        print("Press any key for the next game")
        input()
    bext.clear()
    for player in players:
        if player.state != 6:
            print(f"{player.name} wins the table! All others are just some random bots")

def update_tree():
    pass

def next_parameter(selected_node):
    pass

def backpropagation(root,reward):
    if root.parent!=None:
        root.values+=reward
        root.visits+=1
        backpropagation(root.parent,reward)

def mcts_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised):
    player=players[index]
    turn_dict={0:0,3:1,4:2,5:3}
    turn = turn_dict[len(board.hand.cards)]
    if turn==0:
        player.root_node_tree=MCTS_Node(player.name,0)
        player.mcts_tree=player.root_node_tree
    else:
        player.mcts_tree=update_tree()
        cur_node=player.mcts_tree
    for k in range(1000):
        selected_node=selection(cur_node)
        actions,next_turn,next_player_name=next_parameter(selected_node)
        expansion(selected_node,actions,next_turn,next_player_name)
        reward=simulation(selected_node)
        backpropagation(root,reward)
    actions=choose_actions(cur_node)
    return [actions]