import Poker_component

def print_board(players,board):
    print("--------------")
    for player in players:
        if player.state not in [4,5,6]:
            print(player)
    print(board)
    print("--------------")
    
def game_human_vs_human(num_players,init_money):
    indicator=0
    count=1
    playing=num_players
    table_condition=True
    players=[]
    big_blind=num_players-1
    for x in range(num_players):
        players.append(Poker_component.Player(None,f"Player {x+1}",init_money))
    while table_condition:
        print(f"""--------------
Game {count}
--------------""")
        a=Poker_component.Deck()
        hands=a.deal_hands(playing,2)
        board=Poker_component.Player(Poker_component.Hand(),"Board", 0)
        for x in range(playing):
            if players[x].state!=6:
                players[x].hand=hands.pop()
                players[x].state=-1
                print(players[x])
        turn=["Preflop","Flop","Turn","River"]
        cur_call,last_raised,cur_raise,board.money=PREFLOP_BIG_BLIND,players[big_blind].name,PREFLOP_BIG_BLIND,PREFLOP_BIG_BLIND
        players[big_blind].money-=PREFLOP_BIG_BLIND
        players[big_blind].pot=PREFLOP_BIG_BLIND
        players[big_blind].state=2
        folded=0
        for k in range(4):
            if k!=0:
                cur_call,last_raised,cur_raise=0,players[big_blind],0
                for player in players:
                    if player.state not in [0,3,4,5,6]:
                        player.pot=0
                        player.state=-1
            temp=cur_call
            match=0
            print(turn[k])
            if k==0:
                print(f"{players[-1].name} is big blind and put in 10$")
            if k>=2:
                board.hand.add_card(a.deal_cards())
                print_board(players,board)
            elif k==1:
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                print_board(players,board)
            conditioner=True
            index=(big_blind+1)%num_players
            while conditioner:
                if players[index].state in [-1,1,2]:
                    cur_call,last_raised,board.money,cur_raise=players[index].action(indicator,cur_call,last_raised,board.money,cur_raise)
                if players[index].state==4:
                    players[index].state=5
                    folded+=1
                    if folded==playing-1:
                        conditioner=False
                        break
                if temp==cur_call:
                    match+=1
                    if match==num_players-folded:
                        conditioner=False
                        break
                else:
                    match=1
                    temp=cur_call
                index=(index+1)%num_players
        checker=[]
        for player in players:
            if player.state in [0,1]:
                checker.append(player.hand.create_poker(board.hand).check())
        win=max(checker)
        winner=[]
        for checker_items in checker:
            if checker_items==win:
                winner.append(1)
            else:
                winner.append(0)
        hehe=", ".join([f"Player {x}" for x in range(1,len(winner)+1) if winner[x-1]])
        money_win=board.money//sum(winner)
        for x in range(len(winner)):
            if winner[x]:
                players[x].money+=money_win
        print(hehe+" win the game!")
        for player in players:
            if player.money==0:
                player.state=3
            if player.state==3:
                print(f"{player.name} broke as hell!")
                player.state=6
                playing-=1
        if playing==1:
            break
        count+=1
        big_blind=(big_blind+1)%num_players
        while players[big_blind].state==6:
            big_blind=(big_blind+1)%num_players
    for player in players:
        if player.state!=6:
            print(f"{player.name} wins the table! All others are just some random bots")
PREFLOP_BIG_BLIND=10

                
game_human_vs_human(3,100)
    
