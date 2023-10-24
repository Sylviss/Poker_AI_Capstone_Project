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
def game_human_vs_autobot(num_players):
    a=Poker_component.Deck()
    players=a.deal_hands(num_players,2)
    for player in players:
        print(player)
        print()
    
