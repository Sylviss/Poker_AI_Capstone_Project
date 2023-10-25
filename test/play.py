import Poker_component
def game(num_players):
    a=Poker_component.Deck()
    players=a.deal_hands(num_players,2)
    hands=[]
    board=a.deal_hands(1,5)[0]
    for x in range(len(players)):
        hands.append(players[x].create_poker(board).check())
        print(f"Player {x+1}")
        print(players[x])
        print()
    print(board)
    a=max(hands)
    winner=[]
    for hand in hands:
        if hand==a:
            winner.append(1)
        else:
            winner.append(0)
    hehe=", ".join([f"Player {x}" for x in range(1,len(winner)+1) if winner[x-1]])
    print(hehe+" win the game!")


def print_board(players,board):
    print("--------------")
    for player in players:
        print(player)
    print(board)
    print("--------------")
    
def game_human_vs_human(num_players,init_money):
    indicator=0
    cur_call=0
    last_raised=""
    cur_raise=0
    a=Poker_component.Deck()
    hands=a.deal_hands(num_players,2)
    players=[]
    board=Poker_component.Player(Poker_component.Hand(),"Board", 0)
    for x in range(len(hands)):
        players.append(Poker_component.Player(hands[x],f"Player {x+1}",init_money))
        print(players[-1])
    turn=["Preflop","Flop","Turn","River"]
    for k in range(4):
        if k==0:
            cur_call,last_raised,cur_raise=10,"Player 1",10
        else:
            cur_call,last_raised,cur_raise=0,"Player 1",0
            for player in players:
                player.pot=0
        print(turn[k])
        if k>=2:
            board.hand.add_card(a.deal_cards())
            print_board(players,board)
        elif k==1:
            board.hand.add_card(a.deal_cards())
            board.hand.add_card(a.deal_cards())
            board.hand.add_card(a.deal_cards())
            print_board(players,board)
        conditioner=True
        while conditioner:
            for player in players:
                if player.state in [-1,1,2]:
                    cur_call,last_raised,board.money,cur_raise=player.action(indicator,cur_call,last_raised,board.money,cur_raise)
                if last_raised==player.name and player.state!=2:
                    conditioner=False
                    break
    checker=[]
    for player in players:
        if player.state in [0,1]:
            checker.append(player.create_poker(board).check())
    win=max(checker)
    winner=[]
    for hand in hands:
        if hand==win:
            winner.append(1)
        else:
            winner.append(0)
    hehe=", ".join([f"Player {x}" for x in range(1,len(winner)+1) if winner[x-1]])
    print(hehe+" win the game!")
    for player in players:
        if player.money==0:
            player.state=3
        if player.state==3:
            print(f"{player.name} broke as hell!")
            player.state=5
            
game_human_vs_human(2,100)
    
