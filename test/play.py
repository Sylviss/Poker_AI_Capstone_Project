import Poker
def game(num_players):
    a=Poker.Deck()
    players=a.deal_hands(num_players,2)
    board=a.deal_hands(1,5)[0]
    return 0
game(3)