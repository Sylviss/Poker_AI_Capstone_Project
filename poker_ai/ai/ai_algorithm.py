import random
from poker_ai.ai.eval_func import eval_func

##################################
#Constant

DECIDER=10
CONFIDENT_RANGE=0.3 # should be < 0.5



##################################



def simple_ai_agent(player, num_players, board, actions,cur_call,cur_raise,min_pot):
    """Return the actions that the AI do base on the list of actions that it can do.

    Args:
        player (poker_ai.poker.poker_component.Player()): the Player object of the AI , which contains the hand cards.
        num_players (int): the number of active player in the game. Required as the chance of winning decrese when the table has more player.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
        actions (list(int)): the list of actions that the AI can do, represent by integers.
        cur_call (int): current call value of the phase.
        cur_raise (int): current raise value of the phase.

    Returns:
        int: the actions that the AI do.
    """
    win,draw=eval_func(player, num_players, board)
    draw+=win
    decides=[]
    for _ in range(DECIDER):
        decides.append(random.random())
    decide=sum(decides)/DECIDER
    if decide>draw:
        if 2 in actions:
            return [2]
        elif 3 in actions and cur_call-player.pot<=(1-decide)/(1-draw)*CONFIDENT_RANGE*player.money:
            return [3]
        else:
            return [5]
    elif decide<=draw and decide>=win:
        if 2 in actions:
            return [2]
        elif 3 in actions:
            if cur_call-player.pot<=CONFIDENT_RANGE*player.money:
                return [3]
            else:
                return [5]
        else:
            return [5]
    elif decide>=win*(1-CONFIDENT_RANGE):
        if 4 in actions and cur_call-player.pot<=CONFIDENT_RANGE*player.money:
            raise_value=cur_raise+(min_pot-cur_raise)*random.random()*(decide-win*CONFIDENT_RANGE)/(win*(1-CONFIDENT_RANGE))
            return [4,int(raise_value)]
        elif 3 in actions:
            return [3]
        elif 2 in actions:
            return [2]
        else:
            return [5]
    elif decide>=win*CONFIDENT_RANGE:
        if 4 in actions and cur_call-player.pot<=CONFIDENT_RANGE*player.money:
            raise_value=cur_raise+(min_pot-cur_raise)*(decide-win*CONFIDENT_RANGE)/(win*(1-CONFIDENT_RANGE))
            return [4,int(raise_value)]
        else:
            return [1]
    else:
        return [1]
            
def action_ai_model(self,cur_call,last_raised,board_pot,cur_raise,num_players,board,min_pot):
    """Make the AI act ingame. Use the basic AI model.

    Args:
        cur_call (int): current call value of the phase.
        last_raised (string): the player.name of the last player that raise the pot.
        board_pot (int): current pot of the board.
        cur_raise (int): current raise value of the phase.
        num_players (int): the number of active player in the game.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.

    Returns:
        tuple: to change some value inside the function and then pass that value outside, because Python don't have a fking pointer!
    """
    checkout=[1,5]
    ans=0
    if cur_call==self.pot:
        checkout.append(2)
    elif cur_call>self.pot and self.money>cur_call-self.pot:
        checkout.append(3)
    if self.money>cur_call-self.pot+cur_raise:
        checkout.append(4)
    print(f"{self.name} need to put in at least {cur_call-self.pot}$")
    agent=simple_ai_agent(self, num_players, board, checkout,cur_call,cur_raise,min_pot)
    a=agent[0]
    print(f"Bot choose {a}")
    if a==1:
        if self.money<=cur_call-self.pot:
            ans=self.all_in_1(cur_call,last_raised,board_pot,cur_raise)
        else:
            ans=self.all_in_2(cur_call,last_raised,board_pot,cur_raise)
    elif a==2:
        ans=self.check(cur_call,last_raised,board_pot,cur_raise)
    elif a==3:
        ans=self.call(cur_call,last_raised,board_pot,cur_raise)
    elif a==4:
        b=agent[1]
        ans=self.raise_money(b,cur_call,last_raised,board_pot,cur_raise)
    elif a==5:
        ans=self.fold(cur_call,last_raised,board_pot,cur_raise)
    return ans
