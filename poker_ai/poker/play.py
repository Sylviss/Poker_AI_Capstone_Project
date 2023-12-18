import bext,json
from poker_ai.poker import poker_component
from poker_ai.ai.ai_algorithm import action_ai_model
from poker_ai.constant import STOP,PREFLOP_BIG_BLIND,INDICATOR,MULTIPROCESS,TURN_TO_RAISE_POT,DEBUG_MODE
from poker_ai.ai.ml.opponent_modelling import Data_table, opponent_modelling, table_counting, table_rescaling


def default_table():
    try:
        f = open("poker_ai/ai/ml/default_data.json")
    except:
        print('No file exist!')
    else:
        data = json.load(f)
        f.close()
        return data

def action(index, players, indicator, cur_call, last_raised, board_pot, cur_raise, num_players, board, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, turn):
    """Choose who will do the actions base on the indicator.

    Args:
        indicator (int): Decide if who shoud do the action, human or AI.
        all the others args are just there to pass to the functions

    Returns:
        action_function: return the function of the one who should do the actions
    """
    self=players[index]
    if indicator == 0:
        return action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, tables, turn, board, num_players)
    elif indicator == 1:
        if self.name == "Player 1":
            return action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, tables, turn, board, num_players)
        return action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, turn)
    else:
        return action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, turn)


def action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, tables, turn, board, num_players):
    """
        types of number:
        1.1: All-in 1: Avalable if self.money <= cur_call-self.pot
        1.2. All-in 2: Avalable if self.money > cur_call-self.pot
        2. Check: Avalable if cur_call == self.pot
        3. Call: Avalable if cur_call > self.pot
        4. Raise: Avalable if self.money > cur_call-self.pot+cur_raise. Must raise at least cur_raise and max almost all in.
        5. Fold: whenever you want it
        6. Raise max: This is a new one.

    Allow a human to act ingame

    Args:
        cur_call (int): current call value of the phase.
        last_raised (string): the player.name of the last player that raise the pot.
        board_pot (int): current pot of the board.
        cur_raise (int): current raise value of the phase.

    Returns:
        tuple: to change some value inside the function and then pass that value outside, because Python don't have a fking pointer!
    """
    checkout = [1, 5]
    stack = ["fold", "all in"]
    word = ["1: all in", "5: fold"]

    if cur_call == self.pot:
        stack.append("check")
        checkout.append(2)
        word.append("2: check")

    elif cur_call > self.pot and self.money > cur_call-self.pot:
        stack.append("call")
        checkout.append(3)
        word.append("3: call")

    if self.money > cur_call-self.pot+cur_raise:
        stack.append("raise")
        checkout.append(4)
        word.append("4: raise")
    min_money=min([(player.money+player.pot)-cur_call if player.state not in [4,5,6] and (player.money+player.pot)-cur_call>0 else 0 if player.state not in [4,5,6] else 2**31-1 for player in players])
    if min_money!=0 and (self.money+self.pot)-cur_call>min_money:
        stack.append("raise max")
        checkout.append(6)
        word.append("6: raise max")
    print(f"{self.name} need to put in at least {cur_call-self.pot}$")
    opponent_modelling(gamelogger.history, tables, turn, players[0], board, num_players, checkout)

    while True:
        print("Choose between:")
        print(", ".join(word))
        try:
            action = int(input('>>> '))
        except ValueError:
            continue
        if action not in checkout:
            continue
        break

    if action == 1:
        gamelogger.keylogging(self, [1])
        if self.money <= cur_call-self.pot:
            ans = self.all_in_1(cur_call, last_raised,
                                board_pot, cur_raise)
        else:
            ans = self.all_in_2(cur_call, last_raised,
                                board_pot, cur_raise)
            
    elif action == 2:
        gamelogger.keylogging(self, [2])
        ans = self.check(cur_call, last_raised, board_pot, cur_raise)

    elif action == 3:
        gamelogger.keylogging(self, [3,(cur_call-self.pot)/self.money])
        ans = self.call(cur_call, last_raised, board_pot, cur_raise)

    elif action == 4:
        while True:
            print(
                f"Please choose between {cur_raise}$ and {self.money-1-(cur_call-self.pot)}$")
            try:
                b = int(input('>>> '))
            except ValueError:
                continue
            if b < cur_raise or b > self.money-1-(cur_call-self.pot):
                continue
            ans = self.raise_money(
                b, cur_call, last_raised, board_pot, cur_raise)
            gamelogger.keylogging(self, [4,(b+cur_call-self.pot)/self.money])
            break

    elif action == 5:
        gamelogger.keylogging(self, [5])
        ans = self.fold(cur_call, last_raised, board_pot, cur_raise)
    elif action == 6:
        gamelogger.keylogging(self, [6,(min_money+cur_call-self.pot)/self.money])
        ans = self.raise_money(
                min_money, cur_call, last_raised, board_pot, cur_raise)
    return ans


def print_blind_board(players, board, indicator=INDICATOR):
    """Print the board without showing the other player's cards

    Args:
        players (list(poker_ai.poker.poker_component.Player())): a list contains all the players.
        board (poker_ai.poker.poker_component.Player()): the Player object of the board, which contains the community cards.
    """
    if indicator == 1:
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

def game_but_cheaty(num_players, init_money, cards):
    """Play a game with {num_players} player with {init_money} base money. It's just that we choose the card ourself.

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
        gamelogger=poker_component.Gamelogger(players)
        if count % TURN_TO_RAISE_POT == 1:
            preflop_big_blind_value = PREFLOP_BIG_BLIND * \
                int((2**(count//TURN_TO_RAISE_POT)))
            preflop_small_blind_value = preflop_big_blind_value//2
        deck = poker_component.Deck()
        for str_repr in cards[::-1]:
            card=poker_component.str_to_card(str_repr)
            deck.cards.remove(card)
            deck.cards.insert(0,card)
        hands = deck.deal_hands(playing, 2)
        board = poker_component.Player(
            poker_component.Hand(), "Board", temp_board_money)
        for x in range(num_players):
            players[x].pot = 0
            if players[x].state != 6:
                players[x].hand = hands.pop(0)
                players[x].state = -1
        print_blind_board(players, board)
        turn = ["Preflop", "Flop", "Turn", "River"]
        folded = 0
        for k in range(4):
            gamelogger.next_turn()
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
                board.hand.add_card(deck.deal_cards())
                print_blind_board(players, board)
            elif k == 1:
                board.hand.add_card(deck.deal_cards())
                board.hand.add_card(deck.deal_cards())
                board.hand.add_card(deck.deal_cards())
                print_blind_board(players, board)
            conditioner = True
            index = (big_blind+1) % num_players
            while conditioner:
                if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                    conditioner = False
                    break
                if players[index].state in [-1, 1, 2]:
                    cur_call, last_raised, board.money, cur_raise = action(
                        index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value)
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
            if DEBUG_MODE==1:
                print("Post-game")
                print_board(players, board)
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
            print(f"{player.name} wins the table! All others are just some random bots")

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
    tables = {}
    big_blind = num_players-1
    small_blind = num_players-2
    temp_board_money = 0
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money))
        tables[players[-1].name] = Data_table()
    try:
        f = open("poker_ai/ai/ml/play_data.json")
    except:
        for x in range(num_players):
            tables[players[-1].name] = Data_table()
    else:
        datas = json.load(f)
        for player in datas:
            tables[player] = Data_table()
            tables[player].counting_table = datas[player]
            tables[player].count = table_counting(tables[player].counting_table)
        f.close()
    while table_condition:
        print(f"""*** *** ***\nGame {count}\n*** *** ***""")
        gamelogger=poker_component.Gamelogger(players)
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
            gamelogger.next_turn()
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
                        index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, k)
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
            if DEBUG_MODE==1:
                print("Post-game")
                print_board(players, board)
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
            print(f"{player.name} wins the table! All others are just some random bots")        
            datas = {}
            for _player in tables:
                datas[_player] = tables[_player].counting_table
            with open("poker_ai/ai/ml/play_data.json", 'w') as file:
                json.dump(datas, file)
                file.close()

def fast_testing(num_players, init_money, model_list):
    """Play a game with {num_players} player with {init_money} base money
    Some changes:
        + This return the winner's name
        + Always be all bot

    Args:
        num_players (int): the number of players
        init_money (int): the number of base money
        model_list (list): list of models for all players
    """    """"""
    indicator = 2
    count = 1
    playing = num_players
    table_condition = True
    players = []
    tables ={}
    big_blind = num_players-1
    small_blind = num_players-2
    temp_board_money = 0
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money,model=model_list[x]))
        tables[players[-1].name] = Data_table()
    try:
        f = open("poker_ai/ai/ml/play_data.json")
    except:
        for x in range(num_players):
            tables[players[-1].name] = Data_table()
    else:
        datas = json.load(f)
        for player in datas:
            tables[player] = Data_table()
            tables[player].counting_table = datas[player]
            tables[player].count = table_counting(tables[player].counting_table)
        f.close()
    while table_condition:
        print(f"""*** *** ***\nGame {count}\n*** *** ***""")
        gamelogger=poker_component.Gamelogger(players)
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
        print_blind_board(players, board, 2)
        turn = ["Preflop", "Flop", "Turn", "River"]
        folded = 0
        for k in range(4):
            gamelogger.next_turn()
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
                print_blind_board(players, board, 2)
            elif k == 1:
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                print_blind_board(players, board, 2)
            conditioner = True
            index = (big_blind+1) % num_players
            while conditioner:
                if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                    conditioner = False
                    break
                if players[index].state in [-1, 1, 2]:
                    cur_call, last_raised, board.money, cur_raise = action(
                        index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, k)
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
    for player in players:
        if player.state != 6:
            print(f"{player.name} wins the table! All others are just some random bots")
            datas = {}
            for _player in tables:
                datas[_player] = tables[_player].counting_table
            with open("poker_ai/ai/ml/play_data.json", 'w') as file:
                json.dump(datas, file)
                file.close()
            return player.name
        
def dataset_logging(num_players, init_money, model_list):
    """Play a game with {num_players} player with {init_money} base money
    Some changes:
        + This return the winner's name
        + Always be all bot

    Args:
        num_players (int): the number of players
        init_money (int): the number of base money
        model_list (list): list of models for all players
    """    """"""
    indicator = 2
    with open("poker_ai/datasets/num.json","r") as num: 
        count = json.load(num) 
    log_dict={}
    log_dict["game_id"]=count
    log_dict["players"]=[]
    playing = num_players
    table_condition = True
    players = []
    big_blind = num_players-1
    small_blind = num_players-2
    temp_board_money = 0
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money,model=model_list[x]))
    while table_condition:
        print(f"""*** *** ***\nGame {count}\n*** *** ***""")
        gamelogger=poker_component.Gamelogger(players)
        preflop_big_blind_value = PREFLOP_BIG_BLIND
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
            log_dict["players"].append({"seat":x+1,"player_name":players[x].name,"start_money":init_money, "player_hand":[players[x].hand.cards[0].printcardsimple(),players[x].hand.cards[1].printcardsimple()]})
        print_blind_board(players, board, 2)
        log_dict["actions"]={}
        folded = 0
        log_dict["small_blind"]=players[small_blind].name
        log_dict["big_blind"]=players[big_blind].name
        log_dict["small_blind_value"]=preflop_small_blind_value
        log_dict["big_blind_value"]=preflop_big_blind_value
        for k in range(4):
            gamelogger.next_turn()
            if k != 0:
                last_raised, cur_raise = None, preflop_big_blind_value
                for player in players:
                    if player.state not in [0, 3, 4, 5, 6]:
                        player.state = -1
            match = 0
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
                print_blind_board(players, board, 2)
            elif k == 1:
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                board.hand.add_card(a.deal_cards())
                print_blind_board(players, board, 2)
            conditioner = True
            index = (big_blind+1) % num_players
            turn=len(board.hand.cards)
            log_dict["actions"][turn]=[]
            while conditioner:
                if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                    conditioner = False
                    break
                prev_money=players[index].money
                call_value=cur_call-players[index].pot
                if players[index].state in [-1, 1, 2]:
                    cur_call, last_raised, board.money, cur_raise = action(
                        index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value)
                if players[index].state in [0,1,2,4]:
                    if players[index].state==0:
                        log_action=[players[index].name,[1,0]]
                    elif players[index].state==4:
                        log_action=[players[index].name,[5,0]]
                    elif players[index].state==1:
                        if call_value==0:
                            log_action=[players[index].name,[2,0]]
                        else:
                            log_action=[players[index].name,[3,0]]
                    else:
                        log_action=[players[index].name,[4,prev_money-players[index].money-call_value]]
                log_dict["actions"][turn].append(log_action)
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
                    hehe = [player.name]
                    log_dict["winner"] = hehe[:]
                    log_dict["board"]=[card.printcardsimple() for card in board.hand.cards]
                    player.money += board.money
                    board.money = 0
                    break
            for player in players:
                if player.money < 0:
                    raise poker_component.WTF
                if player.money == 0 and player.state != 6:
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
            for idx in range(len(players)):
                log_dict["players"][idx]["after_money"]=players[idx].money
                log_dict["players"][idx]["delta_money"]=players[idx].money-init_money
            with open("poker_ai/datasets/num.json","w") as num: 
                json.dump(count,num) 
            with open("poker_ai/datasets/new_datasets_2p.json","a+") as num: 
                json.dump(log_dict,num) 
                num.write(",")
            return
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
        hehe = [players[x].name for x in range(len(winner)) if winner[x]]
        log_dict["winner"] = hehe[:]
        log_dict["board"]=[card.printcardsimple() for card in board.hand.cards]
        money_win = board.money//sum(winner)
        temp_board_money = board.money-money_win*sum(winner)
        for x in range(len(winner)):
            if winner[x]:
                players[x].money += money_win
        for player in players:
            if player.money < 0:
                raise poker_component.WTF
            if player.money == 0 and player.state != 6:
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
        for idx in range(len(players)):
            log_dict["players"][idx]["after_money"]=players[idx].money
            log_dict["players"][idx]["delta_money"]=players[idx].money-init_money
        with open("poker_ai/datasets/num.json","w") as num: 
            json.dump(count,num) 
        with open("poker_ai/datasets/new_datasets_2p.json","a+") as num: 
            json.dump(log_dict,num) 
            num.write(",")
        return
