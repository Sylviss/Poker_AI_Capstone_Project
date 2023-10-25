import poker_component  

###############################################
#Constant:

PREFLOP_BIG_BLIND=10
INDICATOR=2 #0 is for testing against all human-controlled; 1 is for bot: Player 1 will be human, all others will be bot; 2 is all bot for testing purpose
PLAYER=10
INIT_MONEY=100



################################################

def print_board(players,board):
    print("--------------")
    for player in players:
        if player.state not in [4,5,6]:
            print(player)
        elif player.state!=6:
            print(f"{player.name}: {player.money}$")
            print('Folded')
            print()
    print(board)
    print("--------------")
    
def game(num_players,init_money):
    indicator=INDICATOR
    count=1
    playing=num_players
    table_condition=True
    players=[]
    big_blind=num_players-1
    temp_board_money=0
    for x in range(num_players):
        players.append(poker_component.Player(None,f"Player {x+1}",init_money))
    while table_condition:
        print(f"""--------------\nGame {count}\n--------------""")
        a=poker_component.Deck()
        hands=a.deal_hands(playing,2)
        board=poker_component.Player(poker_component.Hand(),"Board", temp_board_money)
        for x in range(num_players):
            if players[x].state!=6:
                players[x].hand=hands.pop()
                players[x].state=-1
                players[x].pot=0
                print(players[x])
        turn=["Preflop","Flop","Turn","River"]
        folded=0
        for k in range(4):
            if k!=0:
                cur_call,last_raised,cur_raise=0,None,0
                for player in players:
                    if player.state not in [0,3,4,5,6]:
                        player.pot=0
                        player.state=-1
            match=0
            print(turn[k])
            if k==0:
                if players[big_blind].money<=PREFLOP_BIG_BLIND:
                    players[big_blind].pot=players[big_blind].money
                    players[big_blind].money=0
                    players[big_blind].state=0
                    print(f"{players[big_blind].name} is big blind and put in {players[big_blind].pot}$")
                    cur_call,last_raised,cur_raise=players[big_blind].pot,None,players[big_blind].pot
                    board.money+=players[big_blind].pot
                else:
                    players[big_blind].money-=PREFLOP_BIG_BLIND
                    players[big_blind].pot=PREFLOP_BIG_BLIND
                    print(f"{players[big_blind].name} is big blind and put in {PREFLOP_BIG_BLIND}$")
                    cur_call,last_raised,cur_raise=PREFLOP_BIG_BLIND,None,PREFLOP_BIG_BLIND
                    board.money+=PREFLOP_BIG_BLIND
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
                if last_raised==players[index].name and (players[index].state==2 or players[index].state==0):
                    conditioner=False
                    break
                if players[index].state in [-1,1,2]:
                    cur_call,last_raised,board.money,cur_raise=players[index].action(indicator,cur_call,last_raised,board.money,cur_raise)
                if players[index].state==4:
                    players[index].state=5
                    folded+=1
                    if folded>=playing-1:
                        conditioner=False
                        break
                if players[index].state!=6:
                    match+=1
                if (match==playing and last_raised is None):
                    conditioner=False
                    break
                index=(index+1)%num_players
            if folded==playing-1:
                break
        if folded==playing-1:
            for player in players:
                if player.state not in [3,4,5,6]:
                    print(f"{player.name} win the game!")
                    player.money+=board.money
                    board.money=0
                    break
            for player in players:
                if player.money==0 and player.state!=6:
                    player.state=3
                if player.state==3:
                    print(f"{player.name} broke as hell!")
                    player.state=6
                    playing-=1
            count+=1
            big_blind=(big_blind+1)%num_players
            while players[big_blind].state==6:
                big_blind=(big_blind+1)%num_players
            if playing==1:
                table_condition=False
                break
            # print("Press any key for the next game")
            # input()
            continue
        checker=[]
        for player in players:
            if player.state in [0,1,2]:
                checker.append(player.hand.create_poker(board.hand).check())
            else:
                checker.append((0,0))
        win=max(checker)
        winner=[]
        for checker_items in checker:
            if checker_items==win:
                winner.append(1)
            else:
                winner.append(0)
        hehe=", ".join([f"Player {x}" for x in range(1,len(winner)+1) if winner[x-1]])
        money_win=board.money//sum(winner)
        temp_board_money=board.money-money_win*sum(winner)
        for x in range(len(winner)):
            if winner[x]:
                players[x].money+=money_win
        print(hehe+" win the game!")
        for player in players:
            if player.money==0 and player.state!=6:
                player.state=3
            if player.state==3:
                print(f"{player.name} broke as hell!")
                player.state=6
                playing-=1
        count+=1
        big_blind=(big_blind+1)%num_players
        while players[big_blind].state==6:
            big_blind=(big_blind+1)%num_players
        if playing==1:
            table_condition=False
            break
        # print("Press any key for the next game")
        # input()
        
    for player in players:
        if player.state!=6:
            print(f"{player.name} wins the table! All others are just some random bots")
            print(f"{player.money}")

game(PLAYER,INIT_MONEY)

