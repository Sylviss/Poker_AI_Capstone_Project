import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func
from poker_ai.constant import DECIDER,CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN,CALL_RANGE,BLUFF_RANGE

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

def mcs_and_prob_based_ai_agent(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised):
    """Return the actions that the AI do base on the list of actions that it can do.

    Args:
        player (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
        actions (list(int)): the list of actions that the AI can do, represent by integers.
        cur_call (int): current call value of the phase.
        cur_raise (int): current raise value of the phase.
        mul_indicator (int): use multi-process evaluation function or not.

    Returns:
        int: the actions that the AI do.
    """ 
    player=players[index]
    rule_dict={0:0.85,3:0.9,4:0.95,5:1}
    betted_dict={0:1,1:0.95}
    if last_raised is None:
        betted=betted_dict[0]
    else:
        betted=betted_dict[1]
    turn = len(board.hand.cards)
    draw_rate = (1-(1-DRAW)*rule_dict[turn])*betted
    win_rate = (1-(1-WIN)*rule_dict[turn])*betted
    if betted==1:
        raise_multipler={0:1,3:1.5,4:2,5:2.5}
    else:
        raise_multipler={0:1,3:1,4:1,5:1}
    if mul_indicator == 0:
        win, draw = eval_func(player, num_players, board)
    else:
        win, draw = multi_process_eval_func(player, num_players, board)
    draw += win
    decides = []
    for _ in range(DECIDER):
        decides.append(random.random())
    pot_odd = (cur_call - player.pot) / (cur_call - player.pot + board.money)
    decide = 1 - (win * 0.75 + draw * 0.1 + sum(decides) / (DECIDER) * 0.15)
    
    if decide >= win_rate:
        randomized_value=random.random()
        if last_raised is None:
            bluff_range=BLUFF_RANGE[1]
        else:
            bluff_range=BLUFF_RANGE[0]
        if randomized_value<bluff_range:
            decide = 0.29
    
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
        if player.money < RISK_RANGE * board.pot:
            return [1]
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
                        if player.money - (cur_call - player.pot) > 3 * cur_raise * raise_multipler[turn]:
                            cur_raise*=raise_multipler[turn]
                            raise_value = cur_raise + cur_raise * (
                                        (1 + random.random()) ** (1 - (decide - win_rate * 0.5 / win_rate * (0.5 - CONFIDENT_RANGE))))
                        
                        else:
                            raise_value = cur_raise + (random.random() ** 2) * (
                                        player.money - cur_call + player.pot - cur_raise) * (
                                                    1 - (decide - win_rate * 0.5 / win_rate * (0.5 - CONFIDENT_RANGE)))
                        return [4, min(int(raise_value),min_money)]
                    elif player.money < RISK_RANGE * board.pot:
                        return [1]
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
                            raise_value = 3*cur_raise + cur_raise * (
                                        (2 + random.random()) ** (1 - (decide - win_rate * (CONFIDENT_RANGE)) / win_rate * (
                                            0.5 - CONFIDENT_RANGE)))
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
                        if player.money - (cur_call - player.pot) > 6 * cur_raise * raise_multipler[turn]:
                            cur_raise*=raise_multipler[turn]
                            raise_value = 3*cur_raise + cur_raise * (
                                        (2 + random.random()) ** (1 - decide / win_rate * CONFIDENT_RANGE))
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
                
def mcts_ai_model(index, players, min_money, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind, last_raised):
    return 0

def action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, mul_indicator, model, big_blind):
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
        big_blind (int): The value of the big blind.

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
        agent = mcs_and_prob_based_ai_agent(index,players,min_money, num_players, board,
                                checkout, cur_call, cur_raise, mul_indicator, big_blind,last_raised)
    elif model == 1:
        agent = super_random_ai_agent(self, checkout, cur_call, cur_raise)
    elif model == 2:
        agent = all_in_ai_agent(checkout)
    elif model == 3:
        agent = mcts_ai_model(index, players, min_money, num_players, board, 
                              checkout, cur_call, cur_raise, mul_indicator, big_blind, last_raised)
    else:
        raise ValueError("Invalid AI model specified.")
    a = agent[0]
    ans = 0
    if a == 1:
        if self.money <= cur_call-self.pot:
            ans = self.all_in_1(cur_call, last_raised, board_pot, cur_raise)
        else:
            ans = self.all_in_2(cur_call, last_raised, board_pot, cur_raise)
    elif a == 2:
        ans = self.check(cur_call, last_raised, board_pot, cur_raise)
    elif a == 3:
        ans = self.call(cur_call, last_raised, board_pot, cur_raise)
    elif a == 4:
        b = agent[1]
        ans = self.raise_money(b, cur_call, last_raised, board_pot, cur_raise)
    elif a == 5:
        ans = self.fold(cur_call, last_raised, board_pot, cur_raise)
    elif a==6:
        ans = self.raise_money(min_money, cur_call, last_raised, board_pot, cur_raise)
    return ans