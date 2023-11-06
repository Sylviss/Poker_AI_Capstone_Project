import bext
from poker_ai.poker import poker_component
from poker_ai.ai.ai_algorithm import action_ai_model

###############################################
# Constant:

STOP = 0
# 0 for stop after every game, 1 to skip stop
PREFLOP_BIG_BLIND = 10
# Value of the big blind pre-bet.
INDICATOR = 1
# 0 is for testing against all human-controlled
# 1 is for bot: Player 1 will be human, all others will be bot
# 2 is all bot for testing purpose
MULTIPROCESS = 1
# 0 is for single-processing, slower
# 1 is for multi-processing, faster and recommended
TURN_TO_RAISE_POT = 5
# Number of turns to increase the big blind pre-bet

################################################


def action(self, indicator, cur_call, last_raised, board_pot, cur_raise, num_players, board):
    """Choose who will do the actions base on the indicator.

    Args:
        indicator (int): Decide if who shoud do the action, human or AI.
        all the others args are just there to pass to the functions

    Returns:
        action_function: return the function of the one who should do the actions
    """
    if indicator == 0:
        return self.action_human(cur_call, last_raised, board_pot, cur_raise)
    elif indicator == 1:
        if self.name == "Player 1":
            return self.action_human(cur_call, last_raised, board_pot, cur_raise)
        return action_ai_model(self, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS)
    else:
        return action_ai_model(self, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS)


def print_blind_board(players, board):
    """Print the board without showing the other player's cards

    Args:
        players (list(poker_ai.poker.poker_component.Player())): a list contains all the players.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    """
    if INDICATOR == 1:
        print("-"*30)
        for player in players:
            if player.state not in [4, 5, 6] and player.name == "Player 1":
                print(player)
            elif player.state not in [4, 5, 6] and player.name != "Player 1":
                print(f"{player.name}: {player.money}$")
                print('\n'.join([' ___   ___ ', '|## | |## |',
                      '|###| |###|', '|_##| |_##|']))
                print()
            elif player.state != 6:
                print(f"{player.name}: {player.money}$")
                print('Folded')
                print()
        print(board)
        print("-"*30)
    else:
        print_board(players, board)


def print_board(players, board):
    """Print the board without showing the other player's cards

    Args:
        players (list(poker_ai.poker.poker_component.Player())): a list contains all the players.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    """
    print("-"*30)
    for player in players:
        if player.state not in [4, 5, 6]:
            print(player)
        elif player.state != 6:
            print(f"{player.name}: {player.money}$")
            print('Folded')
            print()
    print(board)
    print("-"*30)


def game(num_players, init_money):
    """Play a game with {num_players} player with {init_money} base money

    Args:
        num_players (int): the number of players
        init_money (int): the number of base money
    """    """"""
    bext.clear()
    bext.title("Bruh poker game")
    indicator = INDICATOR
    count = 1
    playing = num_players
    table_condition = True
    players = []
    big_blind = num_players-1
    small_blind = num_players-2
    temp_board_money = 0
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money))
    while table_condition:
        print(f"""*** *** ***\nGame {count}\n*** *** ***""")
        if count % TURN_TO_RAISE_POT == 1:
            preflop_big_blind_value = PREFLOP_BIG_BLIND * \
                int((2**(count//TURN_TO_RAISE_POT)))
            preflop_small_blind_value = preflop_big_blind_value//2
        a = poker_component.Deck()
        hands = a.deal_hands(playing, 2)
        board = poker_component.Player(
            poker_component.Hand(), "Board", temp_board_money)
        for x in range(num_players):
            players[x].pot = 0
            if players[x].state != 6:
                players[x].hand = hands.pop()
                players[x].state = -1
        print_blind_board(players, board)
        turn = ["Preflop", "Flop", "Turn", "River"]
        folded = 0
        for k in range(4):
            if k != 0:
                last_raised, cur_raise = None, preflop_big_blind_value
                for player in players:
                    if player.state not in [0, 3, 4, 5, 6]:
                        player.state = -1
            match = 0
            print(turn[k])
            if k == 0:
                if players[big_blind].money <= preflop_big_blind_value:
                    players[big_blind].pot = players[big_blind].money
                    players[big_blind].money = 0
                    players[big_blind].state = 0
                    print(
                        f"{players[big_blind].name} is big blind and put in {players[big_blind].pot}$")
                    cur_call, last_raised, cur_raise = players[big_blind].pot, None, players[big_blind].pot
                    board.money += players[big_blind].pot
                else:
                    players[big_blind].money -= preflop_big_blind_value
                    players[big_blind].pot = preflop_big_blind_value
                    print(
                        f"{players[big_blind].name} is big blind and put in {preflop_big_blind_value}$")
                    cur_call, last_raised, cur_raise = preflop_big_blind_value, None, preflop_big_blind_value
                    board.money += preflop_big_blind_value
                if players[small_blind].money <= preflop_small_blind_value:
                    players[small_blind].pot = players[small_blind].money
                    players[small_blind].money = 0
                    players[small_blind].state = 0
                    print(
                        f"{players[small_blind].name} is small and put in {players[small_blind].pot}$")
                    board.money += players[small_blind].pot
                else:
                    players[small_blind].money -= preflop_small_blind_value
                    players[small_blind].pot = preflop_small_blind_value
                    print(
                        f"{players[small_blind].name} is small blind and put in {preflop_small_blind_value}$")
                    board.money += preflop_small_blind_value
                if players[big_blind].pot < players[small_blind].pot:
                    cur_call, last_raised, cur_raise = preflop_small_blind_value, None, preflop_small_blind_value
            if k >= 2:
                board.hand.add_card(a.deal_cards())
                print_blind_board(players, board)
            elif k == 1:
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                print_blind_board(players, board)
            conditioner = True
            index = (big_blind+1) % num_players
            while conditioner:
                if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                    conditioner = False
                    break
                if players[index].state in [-1, 1, 2]:
                    cur_call, last_raised, board.money, cur_raise = action(
                        players[index], indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board)
                if players[index].state == 4:
                    players[index].state = 5
                    folded += 1
                    if folded >= playing-1:
                        conditioner = False
                        break
                if players[index].state != 6:
                    match += 1
                if (match == playing and last_raised is None):
                    conditioner = False
                    break
                index = (index+1) % num_players
            if folded == playing-1:
                break
        if folded == playing-1:
            for player in players:
                if player.state not in [3, 4, 5, 6]:
                    print(f"{player.name} win the game!")
                    player.money += board.money
                    board.money = 0
                    break
            for player in players:
                if player.money < 0:
                    raise poker_component.WTF
                if player.money == 0 and player.state != 6:
                    player.state = 3
                if player.state == 3:
                    print(f"{player.name} broke as hell!")
                    player.state = 6
                    playing -= 1
            count += 1
            big_blind = (big_blind+1) % num_players
            while players[big_blind].state == 6:
                big_blind = (big_blind+1) % num_players
            small_blind = (small_blind+1) % num_players
            while players[small_blind].state == 6 or big_blind == small_blind:
                small_blind = (small_blind+1) % num_players
            if playing == 1:
                table_condition = False
                break
            temp_board_money = 0
            if STOP == 0:
                print("Press any key for the next game")
                input()
            bext.clear()
            continue
        print("Post-game")
        print_board(players, board)
        checker = []
        for player in players:
            if player.state in [0, 1, 2]:
                checker.append(player.hand.create_poker(board.hand).check())
            else:
                checker.append((0, 0))
        win = max(checker)
        winner = []
        for checker_items in checker:
            if checker_items == win:
                winner.append(1)
            else:
                winner.append(0)
        hehe = ", ".join(
            [players[x].name for x in range(len(winner)) if winner[x]])
        money_win = board.money//sum(winner)
        temp_board_money = board.money-money_win*sum(winner)
        for x in range(len(winner)):
            if winner[x]:
                players[x].money += money_win
        print(hehe+" win the game!")
        for player in players:
            if player.money < 0:
                raise poker_component.WTF
            if player.money == 0 and player.state != 6:
                player.state = 3
            if player.state == 3:
                print(f"{player.name} broke as hell!")
                player.state = 6
                playing -= 1
        if playing == 1:
            table_condition = False
            break
        count += 1
        big_blind = (big_blind+1) % num_players
        while players[big_blind].state == 6:
            big_blind = (big_blind+1) % num_players
        small_blind = (small_blind+1) % num_players
        while players[small_blind].state == 6 or big_blind == small_blind:
            small_blind = (small_blind+1) % num_players
        if STOP == 0:
            print("Press any key for the next game")
            input()
        bext.clear()
    for player in players:
        if player.state != 6:
            print(
                f"{player.name} wins the table! All others are just some random bots")