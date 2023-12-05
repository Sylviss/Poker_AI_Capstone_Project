import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func
from poker_ai.poker.poker_component import WTF
from poker_ai.constant import DECIDER,CONFIDENT_RANGE


def simple_ai_agent(player, num_players, board, actions, cur_call, cur_raise, mul_indicator):
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
    if mul_indicator == 0:
        win, draw = eval_func(player, num_players, board)
    else:
        win, draw = multi_process_eval_func(player, num_players, board)
    draw += win
    decides = []
    for _ in range(DECIDER):
        decides.append(random.random())
    pot_odd=(cur_call-player.pot)/(cur_call-player.pot+board.money)
    decide = sum(decides)/(DECIDER)*0.3+pot_odd*0.7
    if decide > draw:
        if 2 in actions:
            return [2]
        elif 3 in actions and cur_call-player.pot <= (1-decide)/(1-draw)*CONFIDENT_RANGE*player.money:
            return [3]
        else:
            return [5]
    elif decide <= draw and decide >= win:
        if 2 in actions:
            return [2]
        elif 3 in actions:
            if cur_call-player.pot <= CONFIDENT_RANGE*player.money:
                return [3]
            else:
                return [5]
        else:
            return [5]
    elif decide >= win*(1-CONFIDENT_RANGE):
        if 4 in actions and cur_call-player.pot <= (1-CONFIDENT_RANGE)*player.money:
            raise_value = cur_raise + (1-CONFIDENT_RANGE)*(player.money-(cur_call-player.pot)-cur_raise)*(
                1-(decide-win*(1-CONFIDENT_RANGE))/win*CONFIDENT_RANGE)
            return [4, int(raise_value)]
        elif 3 in actions:
            return [3]
        elif 2 in actions:
            return [2]
        else:
            return [5]
    elif decide >= win*CONFIDENT_RANGE:
        if 4 in actions and cur_call-player.pot <= player.money:
            raise_value = cur_raise+(player.money-(cur_call-player.pot)-cur_raise)*(
                1-(decide-win*CONFIDENT_RANGE)/(win*(1-2*CONFIDENT_RANGE)))
            return [4, int(raise_value)]
        else:
            return [1]
    else:
        return [1]


def action_ai_model(self, cur_call, last_raised, board_pot, cur_raise, num_players, board, mul_indicator, model):
    """Make the AI act ingame. Use the basic AI model.

    Args:
        cur_call (int): current call value of the phase.
        last_raised (string): the player.name of the last player that raise the pot.
        board_pot (int): current pot of the board.
        cur_raise (int): current raise value of the phase.
        num_players (int): the number of active player in the game.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
        mul_indicator (int): use multi-process evaluation function or not.

    Returns:
        tuple: to change some value inside the function and then pass that value outside, because Python don't have a fking pointer!
    """
    checkout = [1, 5]
    ans = 0
    if cur_call == self.pot:
        checkout.append(2)
    elif cur_call > self.pot and self.money > cur_call-self.pot:
        checkout.append(3)
    if self.money > cur_call-self.pot+cur_raise:
        checkout.append(4)
    print(f"{self.name} need to put in at least {cur_call-self.pot}$")
    if model == 0:
        agent = simple_ai_agent(self, num_players, board,
                                checkout, cur_call, cur_raise, mul_indicator)
    elif model == 1:
        agent = rule_based_with_simulation_ai(self, num_players, board,
                                              checkout, cur_call, cur_raise, mul_indicator)
    else:
        raise WTF
    a = agent[0]
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
    return ans