import random
from poker_ai.ai.eval_func import eval_func, multi_process_eval_func,starting_hand_evaluator
from poker_ai.poker.poker_component import WTF
from poker_ai.constant import DECIDER,CONFIDENT_RANGE,RISK_RANGE,DRAW,WIN

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

def simple_ai_agent(player, num_players, board, actions, cur_call, cur_raise, mul_indicator, big_blind,last_raised):
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
    turn=len(board.hand.cards)
    if turn==0:
        decide = starting_hand_evaluator(player,big_blind,num_players,last_raised,cur_call,board)*0.85 + random.random()*0.15
    else:
        if mul_indicator == 0:
            win, draw = eval_func(player, num_players, board)
        else:
            win, draw = multi_process_eval_func(player, num_players, board)
        draw += win
        decides = []
        for _ in range(DECIDER):
            decides.append(random.random())
        pot_odd=(cur_call-player.pot)/(cur_call-player.pot+board.money)
        decide=1-(win*0.75+draw*0.1+sum(decides)/(DECIDER)*0.15)
    if decide > DRAW:
        if 2 in actions:
            return [2]
        elif 3 in actions:
            if cur_call-player.pot <= CONFIDENT_RANGE*player.money or pot_odd>1-decide:
                return [3]
            else:
                return [5]
        else:
            return [5]
    elif decide <= DRAW and decide >= WIN:
        if 2 in actions:
            return [2]
        elif 3 in actions and pot_odd>decide:
            if cur_call-player.pot <= (1-CONFIDENT_RANGE)*player.money or pot_odd>1-decide:
                return [3]
            else:
                return [5]
        else:
            return [5]
    elif decide >= WIN*(1-CONFIDENT_RANGE):
        if player.money<RISK_RANGE*board.pot:
            return [1]
        elif 3 in actions:
            return [3]
        elif 2 in actions:
            return [2]
        else:
            return [5]
    else:
        if turn!=5 or last_raised is not None:
            if decide>= WIN*0.5:
                if 4 in actions and cur_raise + cur_call - player.pot <= (1-CONFIDENT_RANGE)*player.money:
                    if player.money-(cur_call-player.pot)>3*cur_raise:
                        raise_value = cur_raise + cur_raise*((1+random.random())**(1-(decide-WIN*0.5/WIN*(0.5-CONFIDENT_RANGE))))
                    else:
                        raise_value = cur_raise + (random.random()**2)*(player.money-cur_call+player.pot-cur_raise)*(1-(decide-WIN*0.5/WIN*(0.5-CONFIDENT_RANGE)))
                    return [4, int(raise_value)]
                elif player.money<RISK_RANGE*board.pot:
                    return [1]
                elif 3 in actions:
                    return [3]
                elif 2 in actions:
                    return [2]
                else:
                    return [5]
            elif decide >= WIN*CONFIDENT_RANGE:
                if 4 in actions:
                    if player.money-(cur_call-player.pot)>4*cur_raise:
                        raise_value = 2*cur_raise + cur_raise*((1+random.random())**(1-(decide-WIN*(CONFIDENT_RANGE))/WIN*(0.5-CONFIDENT_RANGE)))
                    else:
                        raise_value = cur_raise + random.random()*(player.money-cur_call+player.pot-cur_raise)*(1-(decide-WIN*(CONFIDENT_RANGE))/WIN*(0.5-CONFIDENT_RANGE))
                    return [4, int(raise_value)]
                else:
                    return [1]
            else:
                if 4 in actions:
                    if player.money-(cur_call-player.pot)>6*cur_raise:
                        raise_value = 3*cur_raise + cur_raise*((2+random.random())**(1-decide/WIN*CONFIDENT_RANGE))
                    else:
                        raise_value = cur_raise + (player.money-cur_call+player.pot-cur_raise)*(1-decide/WIN*CONFIDENT_RANGE)
                    return [4, int(raise_value)]
                else:
                    return [1]
        else:
            if decide>= WIN*0.5:
                if 4 in actions and cur_raise + cur_call - player.pot <= (1-CONFIDENT_RANGE)*player.money:
                    raise_value = cur_raise + random.random()*(player.money-cur_call+player.pot-cur_raise)*(1-(decide-WIN*0.5/WIN*(0.5-CONFIDENT_RANGE)))
                    return [4, int(raise_value)]
                elif player.money<RISK_RANGE*board.pot:
                    return [1]
                elif 3 in actions:
                    return [3]
                elif 2 in actions:
                    return [2]
                else:
                    return [5]
            elif decide >= WIN*CONFIDENT_RANGE:
                if 4 in actions:
                    raise_value = cur_raise + (0.25+random.random()*0.75)*(player.money-cur_call+player.pot-cur_raise)*(1-(decide-WIN*(CONFIDENT_RANGE))/WIN*(0.5-CONFIDENT_RANGE))
                    return [4, int(raise_value)]
                else:
                    return [1]
            else:
                if 4 in actions:
                    raise_value = cur_raise + (0.5+random.random()*0.5)*(player.money-cur_call+player.pot-cur_raise)*(1-decide/WIN*CONFIDENT_RANGE)
                    return [4, int(raise_value)]
                else:
                    return [1]


def action_ai_model(self, cur_call, last_raised, board_pot, cur_raise, num_players, board, mul_indicator, model, big_blind):
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
                                checkout, cur_call, cur_raise, mul_indicator, big_blind,last_raised)
    elif model == 1:
        agent = super_random_ai_agent(self, checkout, cur_call, cur_raise)
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