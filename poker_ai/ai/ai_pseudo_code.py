import math
import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func, create_enumerate_dict, enumerate_func, update_prob_dict, update_weighted_dict
from poker_ai.constant import CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN,CALL_RANGE,BLUFF_RANGE, RULE_DICT, BETTED_DICT

class MCTS_Node:
    def __init__(self, player_name, turn):
        """For the actions initialization:
            0: Fold
            1: Check/call
            2: Raise/All in/Raise max/Raise something blah blah
            
            Also, for the sake of simulation and less branch, the AI will only attempt to raise for 4 times. The 4th time will always be raise max/all in
        """
        self.player_name = player_name
        self.turn = turn
        self.visits = 0
        self.values = 0
        self.children = {}
        
def selection_and_expansion(root, cur_iteration):
    if cur_iteration<1000:
        if len(root.children.values())==0:
            choices=[1,2,3]
            for k in choices:
                root.children[k]=MCTS_Node(next_player_name,turn)
        else:
            choices=root.children.keys()
            next_node=random.choice(choices)
            return selection(root.children[next_node],cur_iteration)
    else:
        ev_list=expected_value_gen(root,root.visits)
        node = max(ev_list,key = lambda a: a[1])
        choices=[1,2,3]
        for k in choices:
            root.children[k]=MCTS_Node(next_player_name,turn)
            
def expected_value_gen(root,visits_p):
    if len(root.children.items())==0:
        ev=root.values/root.visit + 2**0.5*(math.log(visits_p)/root.visit)
        return [(root,ev)]
    else:
        res=[]
        for node in root.children.items():
            res+=expected_value_gen(node,visits_p)
        return res

def simulation(root,visits_p):

def mcts_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised):
    player=players[index]
    turn_dict={0:0,3:1,4:2,5:3}
    turn = turn_dict[len(board.hand.cards)]
    if turn==0:
        player.mcts_tree=MCTS_Node(player.name,0)
    cur_node=player.mcts_tree
    for k in range(1000):
        cur_node.selection(k)
    
    return [5]