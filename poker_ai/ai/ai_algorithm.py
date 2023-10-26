import random
from poker_ai.ai.eval_func import eval_func

##################################
#Constant

DECIDER=10
CONFIDENT_RANGE=0.3



##################################



def simple_ai_agent(player, num_players: int, board, actions,cur_call,cur_raise):
    win,draw=eval_func(player, num_players, board)
    draw+=win
    decides=[]
    for _ in range(DECIDER):
        decides.append(random.random())
    decide=sum(decides)/DECIDER
    print(win,draw,decide)
    if decide>draw:
        if 2 in actions:
            return [2]
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
    elif decide>=win*CONFIDENT_RANGE:
        if 4 in actions:
            if cur_call-player.pot<=CONFIDENT_RANGE*player.money:
                raise_value=cur_raise+(player.money+player.pot-cur_call)*random.random()*(decide-win*CONFIDENT_RANGE)/(win*(1-CONFIDENT_RANGE))
                return [4,int(raise_value)]
            elif 3 in actions:
                return [3]
            elif 2 in actions:
                return [2]
            else:
                return [5]
        else:
            if cur_call-player.pot<=CONFIDENT_RANGE*player.money:
                raise_value=cur_raise+(player.money+player.pot-cur_call)*random.random()*(decide-win*CONFIDENT_RANGE)/(win*(1-CONFIDENT_RANGE))
                return [4,int(raise_value)]
            else:
                return [1]
            
def action_ai_model(self,cur_call,last_raised,board_pot,cur_raise,num_players,board):
    checkout=[1,5]
    ans=0
    if cur_call==self.pot:
        checkout.append(2)
    elif cur_call>self.pot and self.money>cur_call-self.pot:
        checkout.append(3)
    if self.money>cur_call-self.pot+cur_raise:
        checkout.append(4)
    print(f"{self.name} need to put in at least {cur_call-self.pot}$")
    agent=simple_ai_agent(self, num_players, board, checkout,cur_call,cur_raise)
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
