import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func, create_enumerate_dict, enumerate_func, update_prob_dict, update_weighted_dict
from poker_ai.ai.ml.opponent_modelling import Rate_recorder
from poker_ai.constant import CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN,CALL_RANGE,BLUFF_RANGE, RULE_DICT, BETTED_DICT

BLUFF_INDICATOR={}

def all_in_ai_agent(actions):
    """We do this for the meme
    """
    if 6 in actions:
        return [6]
    return [1]

def super_random_ai_agent(player, actions, cur_call, cur_raise):
    """This mf randoms everything.

    Args:
        player (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        actions (list(int)): the list of actions that the AI can do, represent by integers.
        cur_call (int): current call value of the phase.
        cur_raise (int): current raise value of the phase.

    Returns:
        int: the actions that the AI do._
    """
    a=random.choice(actions)
    if a==4:
        b=cur_raise + (player.money-cur_call+player.pot-cur_raise)*random.random()
        return [a,int(b)]
    return [a]

def second_approach_mcs_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised,big_blind_value):
    """
    This function implements the second approach Monte Carlo Simulation (MCS) AI agent for playing poker.
    
    Parameters:
    - index (int): The index of the current player.
    - players (list): A list of Player objects representing all the players in the game.
    - min_money (int): The minimum amount of money required to play.
    - num_players (int): The total number of players in the game.
    - board (Board): An object representing the current state of the game board.
    - actions (list): A list of possible actions that the player can take.
    - cur_call (int): The current call amount.
    - cur_raise (int): The current raise amount.
    - mul_indicator (int): A multiplier indicator.
    - big_blind (int): The amount of the big blind.
    - last_raised (int): The index of the last player who raised.
    - big_blind_value (int): The value of the big blind.
    
    Returns:
    - The result of the rule-based AI agent's decision-making process.
    """

    recorder = Rate_recorder()

    player=players[index]
    if last_raised is None:
        betted=BETTED_DICT[0]
    else:
        betted=BETTED_DICT[1]
    turn = len(board.hand.cards)
    draw_rate = (1-(1-DRAW)*RULE_DICT[turn])*betted
    win_rate = (1-(1-WIN)*RULE_DICT[turn])*betted
    if betted==1:
        raise_multipler={0:1,3:1.5,4:2,5:2.5}
    else:
        raise_multipler={0:1,3:1,4:1,5:1}
    if mul_indicator == 0:
        win, draw = eval_func(player, num_players, board)
    else:
        win, draw = multi_process_eval_func(player, num_players, board)
    draw += win
    pot_odd = (cur_call - player.pot) / (cur_call - player.pot + board.money)
    decide = 1 - (win * 0.75 + draw * 0.1 + random.random() * 0.15)
    recorder.win = win_rate
    if player.name in BLUFF_INDICATOR:
        if BLUFF_INDICATOR[player.name]<turn:
            randomized_value=random.random()
            if last_raised is None:
                bluff_range=BLUFF_RANGE[1]*2
            else:
                bluff_range=BLUFF_RANGE[0]*2
            if randomized_value<bluff_range:
                BLUFF_INDICATOR[player.name]=turn
                decide = 0.29
            else:
                BLUFF_INDICATOR.pop(player.name)
        else:   
            BLUFF_INDICATOR.pop(player.name)
    elif decide >= win_rate:
        randomized_value=random.random()
        if last_raised is None:
            bluff_range=BLUFF_RANGE[1]
        else:
            bluff_range=BLUFF_RANGE[0]
        if randomized_value<bluff_range:
            BLUFF_INDICATOR[player.name]=turn
            decide = 0.29
    return rule_based_ai_agent(player,board,decide,draw_rate,win_rate,actions,pot_odd,cur_call,cur_raise,min_money,turn,raise_multipler,big_blind_value)
    
def first_approach_mcs_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised,big_blind_value):
    """
    This function implements the first approach of the Monte Carlo Simulation (MCS) AI agent in a poker game.

    Parameters:
    - index (int): The index of the current player.
    - players (list): A list of Player objects representing all the players in the game.
    - min_money (int): The minimum amount of money required to play.
    - num_players (int): The total number of players in the game.
    - board (Board): An object representing the current state of the game board.
    - actions (list): A list of possible actions that the player can take.
    - cur_call (int): The current call amount.
    - cur_raise (int): The current raise amount.
    - mul_indicator (int): An indicator for the type of evaluation function to use.
    - big_blind (int): The amount of the big blind.
    - last_raised (int): The index of the last player who raised.
    - big_blind_value (int): The value of the big blind.

    Returns:
    - The result of the rule-based AI agent's decision-making process.

    """

    recorder = Rate_recorder() # for opponent modelling purposes
    
    player=players[index]
    if last_raised is None:
        betted=BETTED_DICT[0]
    else:
        betted=BETTED_DICT[1]
    turn = len(board.hand.cards)
    if betted==1:
        raise_multipler={0:1,3:1.5,4:2,5:2.5}
    else:
        raise_multipler={0:1,3:1,4:1,5:1}
    if mul_indicator == 0:
        win, draw = eval_func(player, num_players, board)
    else:
        win, draw = multi_process_eval_func(player, num_players, board)
    draw += win
    draw_rate = (1-(1-draw)*RULE_DICT[turn])*betted
    win_rate = (1-(1-win)*RULE_DICT[turn])*betted
    pot_odd = (cur_call - player.pot) / (cur_call - player.pot + board.money)
    decide = random.random()
    recorder.win = win_rate
    return rule_based_ai_agent(player,board,decide,draw_rate,win_rate,actions,pot_odd,cur_call,cur_raise,min_money,turn,raise_multipler,big_blind_value)

class MCTS_Node:
    def __init__(self,turn):
        self.win=0
        self.visit_count=0
        self.turn=turn
        self.raise_min=None
        self.raise_mid=None
        self.raise_high=None
        self.call=None
        self.check=None
        self.fold=None

def enumeraion_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, big_blind, last_raised, big_blind_value, gamelogger):

    recorder = Rate_recorder()

    if last_raised is None:
        betted=BETTED_DICT[0]
    else:
        betted=BETTED_DICT[1]
    if betted==1:
        raise_multipler={0:1,3:1.5,4:2,5:2.5}
    else:
        raise_multipler={0:1,3:1,4:1,5:1}
    turn = len(board.hand.cards)
    draw_rate = (1-(1-DRAW)*RULE_DICT[turn])*betted
    win_rate = (1-(1-WIN)*RULE_DICT[turn])*betted
    recorder.win = win_rate
    player=players[index]
    if turn==0:
        player.weighted_dict={}
        player.opponent_prob_dict={opponent.name:{} for opponent in players if opponent.name!=player.name and opponent.state!=6}
        player.opponent_can_act={opponent.name:True for opponent in players if opponent.name!=player.name and opponent.state!=6}
        player.opponent_ingame={opponent.name:True for opponent in players if opponent.name!=player.name and opponent.state!=6}
        player.weighted_dict[turn],prob_dict=create_enumerate_dict(player, board, turn)
        for opponent in players:
            if opponent.state!=6 and opponent.name!=player.name:
                player.opponent_prob_dict[opponent.name][0]=prob_dict.copy()
        update_prob_dict(player, turn, gamelogger)
    else:
        update_weighted_dict(player, board, turn, gamelogger)
        update_prob_dict(player, turn, gamelogger)
    hs_dict={}
    for opponent_index in player.opponent_can_act:
        if player.opponent_ingame[opponent_index]:
            hs_dict[opponent_index]=enumerate_func(player,opponent_index,gamelogger)
    # print(hs_dict,player.opponent_ingame)
    win_list=[hs_dict[key][0] for key in hs_dict]
    draw_list=[hs_dict[key][1] for key in hs_dict]
    win=max(win_list)*0.2+min(win_list)*0.8
    draw=sum(draw_list)/len(draw_list)
    decide=1-(win*0.85+draw*0.15+random.random()*0.15)
    pot_odd = (cur_call - player.pot) / (cur_call - player.pot + board.money)
    if player.name in BLUFF_INDICATOR:
        if BLUFF_INDICATOR[player.name]<turn and decide<0.3:
            randomized_value=random.random()
            if last_raised is None:
                bluff_range=BLUFF_RANGE[1]*2
            else:
                bluff_range=BLUFF_RANGE[0]*2
            if randomized_value<bluff_range:
                BLUFF_INDICATOR[player.name]=turn
                decide = 0.29
            else:
                BLUFF_INDICATOR.pop(player.name)
        else:   
            BLUFF_INDICATOR.pop(player.name)
    elif decide >= win_rate:
        randomized_value=random.random()
        if last_raised is None:
            bluff_range=BLUFF_RANGE[1]
        else:
            bluff_range=BLUFF_RANGE[0]
        if randomized_value<bluff_range:
            BLUFF_INDICATOR[player.name]=turn
            decide = 0.29
    return rule_based_ai_agent(player, board, decide, draw_rate, win_rate, actions, pot_odd, cur_call, cur_raise, min_money, turn, raise_multipler, big_blind_value)

def rule_based_ai_agent(player, board, decide, draw_rate, win_rate, actions, pot_odd, cur_call, cur_raise, min_money, turn, raise_multipler, big_blind_value):
    """
    Implements a rule-based AI agent for making decisions in a poker game. The AI make a decision based on the decision value taken from another AI agent or function.

    Args:
        player: The current player object.
        board: The current board object.
        decide: The decision value for the AI agent.
        draw_rate: The draw rate threshold for the AI agent.
        win_rate: The win rate threshold for the AI agent.
        actions: The available actions for the AI agent.
        pot_odd: The pot odds for the AI agent.
        cur_call: The current call value for the AI agent.
        cur_raise: The current raise value for the AI agent.
        min_money: The minimum money value for the AI agent.
        turn: The current turn in the poker game.
        raise_multipler: The raise multiplier for the AI agent.
        big_blind_value: The value of the big blind in the poker game.

    Returns:
        The action of the AI
    """  
    # print(decide,win_rate,draw_rate)
    if decide > draw_rate:
        if 2 in actions:
            return [2]
        else:
            return [5]
    elif decide <= draw_rate and decide >= win_rate:
        if 2 in actions:
            return [2]
        elif 3 in actions and pot_odd < 1 - decide:
            if cur_call - player.pot <= CALL_RANGE * player.money:
                return [3]
            else:
                return [5]
        else:
            return [5]
    elif decide >= win_rate * (1 - CONFIDENT_RANGE):
        if player.money < RISK_RANGE * board.pot or big_blind_value >= player.money:
            return [6 if 6 in actions else 1]
        elif 3 in actions and pot_odd < 1 - decide:
            return [3]
        elif 2 in actions:
            return [2]
        else:
            return [5]
    else:
        if min_money!=0:
            if turn != 5:
                if decide >= win_rate * 0.5:
                    if 4 in actions and cur_raise + cur_call - player.pot <= (1 - CONFIDENT_RANGE) * player.money:
                        if player.money - (cur_call - player.pot) > 2.5 * cur_raise * raise_multipler[turn]:
                            cur_raise*=raise_multipler[turn]
                            raise_value = 2.5*cur_raise
                        
                        else:
                            raise_value = cur_raise + (random.random() ** 2) * (
                                        player.money - cur_call + player.pot - cur_raise) * (
                                                    1 - (decide - win_rate * 0.5 / win_rate * (0.5 - CONFIDENT_RANGE)))
                        return [4, min(int(raise_value),min_money)]
                    elif player.money < RISK_RANGE * board.pot or big_blind_value >= player.money:
                        return [6 if 6 in actions else 1]
                    elif 3 in actions:
                        return [3]
                    elif 2 in actions:
                        return [2]
                    else:
                        return [5]
                elif decide >= win_rate * CONFIDENT_RANGE:
                    if 4 in actions:
                        if player.money - (cur_call - player.pot) > 6 * cur_raise * raise_multipler[turn]:
                            cur_raise*=raise_multipler[turn]
                            raise_value = 3*cur_raise
                        else:
                            raise_value = cur_raise + random.random() * (
                                        player.money - cur_call + player.pot - cur_raise) * (
                                                    1 - (decide - win_rate * (CONFIDENT_RANGE)) / win_rate * (
                                                        0.5 - CONFIDENT_RANGE))
                        return [4, min(int(raise_value),min_money)]
                    elif 6 in actions:
                        return [6]
                    else:
                        return [1]
                else:
                    if 4 in actions:
                        if player.money - (cur_call - player.pot) > 3.5 * cur_raise * raise_multipler[turn]:
                            cur_raise*=raise_multipler[turn]
                            raise_value = 3.5*cur_raise
                        else:
                            raise_value = cur_raise + (player.money - cur_call + player.pot - cur_raise) * (
                                        1 - decide / win_rate * CONFIDENT_RANGE)
                        return [4, min(int(raise_value),min_money)]
                    else:
                        return [1]
            else:
                if decide >= win_rate * 0.5:
                    if 4 in actions and cur_raise + cur_call - player.pot <= (1 - CONFIDENT_RANGE) * player.money:
                        raise_value = cur_raise + random.random() * (
                                    player.money - cur_call + player.pot - cur_raise) * (
                                                1 - (decide - win_rate * 0.5 / win_rate * (0.5 - CONFIDENT_RANGE)))
                        return [4, min(int(raise_value),min_money)]
                    elif player.money < RISK_RANGE * board.pot:
                        return [1]
                    elif 3 in actions:
                        return [3]
                    elif 2 in actions:
                        return [2]
                    elif 6 in actions:
                        return [6]
                    else:
                        return [5]
                elif decide >= win_rate * CONFIDENT_RANGE:
                    if 4 in actions:
                        raise_value = cur_raise + (0.25 + random.random() * 0.75) * (
                                    player.money - cur_call + player.pot - cur_raise) * (
                                                    1 - (decide - win_rate * (CONFIDENT_RANGE)) / win_rate * (
                                                        0.5 - CONFIDENT_RANGE))
                        return [4, min(int(raise_value),min_money)]
                    elif 6 in actions:
                        return [6]
                    else:
                        return [1]
                else:
                    if 4 in actions:
                        raise_value = cur_raise + (0.5 + random.random() * 0.5) * (
                                    player.money - cur_call + player.pot - cur_raise) * (
                                                    1 - decide / win_rate * CONFIDENT_RANGE)
                        return [4, min(int(raise_value),min_money)]
                    elif 6 in actions:
                        return [6]
                    else:
                        return [1]
        else:
            if 2 in actions:
                return [2]
            elif 3 in actions:
                return [3]
            elif decide < win_rate * 0.5:
                return [1]
            else:
                return [5]
        
    
def mcts_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised):
    
    player=players[index]
    turn_dict={0:0,3:1,4:2,5:3}
    turn = turn_dict[len(board.hand.cards)]
    if turn==0:
        player.mcts_tree=MCTS_Node(turn)
    cur_node=player.mcts_tree
    
    return [5]
    
def action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, mul_indicator, model, big_blind, big_blind_value, gamelogger):
    """
    Make the AI act in the game using the basic AI model.

    Args:
        index (int): The index of the current player.
        players (list): A list of Player objects representing all the players in the game.
        cur_call (int): The current call value of the phase.
        last_raised (str): The name of the last player that raised the pot.
        board_pot (int): The current pot of the board.
        cur_raise (int): The current raise value of the phase.
        num_players (int): The number of active players in the game.
        board (poker_ai.poker.poker_component.Player()): The Player object of the board, which contains the community cards.
        mul_indicator (int): Indicator to use multi-process evaluation function or not.
        model (int): The AI model to use.
        big_blind (int): The location of the big blind player.

    Returns:
        int: The action to be taken by the AI player.
    Raises:
        ValueError: If an invalid AI model is specified.

    """
    self=players[index]
    min_money=min([(player.money+player.pot)-cur_call if player.state not in [4,5,6] and (player.money+player.pot)-cur_call>0 else 0 if player.state not in [4,5,6] else 2**31-1 for player in players])
    checkout = [1,5]
    if min_money!=0 and (self.money+self.pot)-cur_call>min_money:
        checkout.append(6)
    if cur_call == self.pot:
        checkout.append(2)
    elif cur_call > self.pot and self.money > cur_call-self.pot:
        checkout.append(3)
    if self.money > cur_call-self.pot+cur_raise:
        checkout.append(4)
    print(f"{self.name} needs to put in at least {cur_call-self.pot}$")
    if model == 0:
        agent = first_approach_mcs_ai_agent(index,players,min_money, num_players, board,
                                checkout, cur_call, cur_raise, mul_indicator, big_blind,last_raised,big_blind_value)
    elif model == 1:
        agent = second_approach_mcs_ai_agent(index,players,min_money, num_players, board,
                                checkout, cur_call, cur_raise, mul_indicator, big_blind,last_raised,big_blind_value)
    elif model == -1:
        agent = enumeraion_ai_agent(index, players, min_money, num_players, board, 
                                                   checkout, cur_call, cur_raise, big_blind, last_raised,big_blind_value, gamelogger)
    elif model == 4:
        agent = super_random_ai_agent(self, checkout, cur_call, cur_raise)
    elif model == 3:
        agent = all_in_ai_agent(checkout)
    elif model == 2:
        agent = mcts_ai_agent(index, players, min_money, num_players, board, 
                              checkout, cur_call, cur_raise, mul_indicator, big_blind, last_raised)
    else:
        raise ValueError("Invalid AI model specified.")
    a = agent[0]
    ans = 0
    if a == 1:
        if self.money <= cur_call-self.pot:
            gamelogger.keylogging(self,[1])
            ans = self.all_in_1(cur_call, last_raised, board_pot, cur_raise)
        else:
            ans = self.all_in_2(cur_call, last_raised, board_pot, cur_raise)
    elif a == 2:
        gamelogger.keylogging(self,[2])
        ans = self.check(cur_call, last_raised, board_pot, cur_raise)
    elif a == 3:
        gamelogger.keylogging(self,[3,(cur_call-self.pot)/self.money])
        ans = self.call(cur_call, last_raised, board_pot, cur_raise)
    elif a == 4:
        b = agent[1]
        gamelogger.keylogging(self,[4,(b+cur_call-self.pot)/self.money])
        ans = self.raise_money(b, cur_call, last_raised, board_pot, cur_raise)
    elif a == 5:
        gamelogger.keylogging(self,[5])
        ans = self.fold(cur_call, last_raised, board_pot, cur_raise)
    elif a==6:
        gamelogger.keylogging(self,[6,(min_money+cur_call-self.pot)/self.money])
        ans = self.raise_money(min_money, cur_call, last_raised, board_pot, cur_raise)
    return ans
