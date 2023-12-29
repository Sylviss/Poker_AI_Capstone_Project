import bext,json
from poker_ai.poker import poker_component
from poker_ai.ai.ai_algorithm import action_ai_model
from poker_ai.ai.ai_algorithm_om import action_ai_with_om_model
from poker_ai.constant import STOP,PREFLOP_BIG_BLIND,INDICATOR,MULTIPROCESS,TURN_TO_RAISE_POT,DEBUG_MODE
from poker_ai.ai.ml.opponent_modelling import Data_table, magical_four, preprocess_table, recording, table_counting, table_record, table_rescaling
from poker_ai.ai.ml.methods import OM_engine
from colorama import Back, Style

def action(index, players, indicator, cur_call, last_raised, board_pot, cur_raise, num_players, board, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, turn, training=0):
    """Choose who will do the actions base on the indicator.

    Args:
        indicator (int): Decide if who shoud do the action, human or AI.
        all the others args are just there to pass to the functions

    Returns:
        action_function: return the function of the one who should do the actions
    """
    self=players[index]
    
    if indicator == 0:
        return action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, engine, turn, index, board, num_players)
    elif indicator == 1:
        if self.name == "Player 1":
            return action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, engine, turn, index, board, num_players)
        else:
            if self.model in [5,6,7]:
                return action_ai_with_om_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, turn, training)
            else:
                return action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, turn, training)
    else:
        if self.model in [5,6,7]:
            return action_ai_with_om_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, turn, training)
        else:
            return action_ai_model(index, players, cur_call, last_raised, board_pot, cur_raise, num_players, board, MULTIPROCESS, self.model, big_blind, big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, turn, training)

def action_human(self, players, cur_call, last_raised, board_pot, cur_raise, gamelogger, engine, turn, index, board, num_players):
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
        tuple: to change some value inside the function and then pass that value outside.
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
    while True:
        print("Choose between:")
        print(", ".join(word))
        try:
            _action = int(input('>>> '))
        except ValueError:
            continue
        if _action not in checkout:
            continue
        break

    if _action == 1:
        gamelogger.keylogging(self, [1],checkout)
        if self.money <= cur_call-self.pot:
            ans = self.all_in_1(cur_call, last_raised,
                                board_pot, cur_raise)
        else:
            ans = self.all_in_2(cur_call, last_raised,
                                board_pot, cur_raise)
            
    elif _action == 2:
        gamelogger.keylogging(self, [2],checkout)
        ans = self.check(cur_call, last_raised, board_pot, cur_raise)

    elif _action == 3:
        gamelogger.keylogging(self, [3,(cur_call-self.pot)/self.money],checkout)
        ans = self.call(cur_call, last_raised, board_pot, cur_raise)

    elif _action == 4:
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
            gamelogger.keylogging(self, [4,(b+cur_call-self.pot)/self.money,b],checkout)
            break

    elif _action == 5:
        gamelogger.keylogging(self, [5],checkout)
        ans = self.fold(cur_call, last_raised, board_pot, cur_raise)
    elif _action == 6:
        gamelogger.keylogging(self, [6,(min_money+cur_call-self.pot)/self.money,min_money],checkout)
        ans = self.raise_money(
                min_money, cur_call, last_raised, board_pot, cur_raise)
    # tables = recording(tables, gamelogger.history, checkout, players[0].hand, board, num_players)
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
                '''print(f'\n'.join([' ___   ___ ', '|## | |## |',
                      '|###| |###|', '|_##| |_##|']))'''
                print(Back.WHITE + "|###|"+ Style.RESET_ALL +" "+Back.WHITE + "|###|" + Style.RESET_ALL)
                print(Back.WHITE + "|###|"+ Style.RESET_ALL +" "+Back.WHITE + "|###|" + Style.RESET_ALL)
                print(Back.WHITE + "|###|"+ Style.RESET_ALL +" "+Back.WHITE + "|###|" + Style.RESET_ALL)
                print()
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
    engine = OM_engine()
    tables = engine.tables
    big_blind = num_players-1
    small_blind = num_players-2
    temp_board_money = 0
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money,model=model_list[x]))
    try:
        f = open("poker_ai/ai/ml/default_data.json")
    except:
        datas_all = {'2':{}, '4':{}, '6':{}}
        tables = Data_table()
        match num_players:
            case 2:
                datas_all['2'] = tables.counting_table
            case 3:
                datas_all['4'] = tables.counting_table
            case 4:
                datas_all['4'] = tables.counting_table
            case 5:
                datas_all['6'] = tables.counting_table
            case 6:
                datas_all['6'] = tables.counting_table
            case _:
                raise Exception('too many players')
        tables.count = table_counting(tables.counting_table)
    else:
        datas_all = json.load(f)
        match num_players:
            case 2:
                datas = datas_all['2']
            case 3:
                datas = datas_all['4']
            case 4:
                datas = datas_all['4']
            case 5:
                datas = datas_all['6']
            case 6:
                datas = datas_all['6']
            case _:
                raise Exception('too many players')
        tables = Data_table()
        tables.counting_table = datas
        tables.count = table_counting(tables.counting_table)
        f.close()
    while table_condition:
        players,engine = refresh(players,engine)
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
                        index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, tables, k, training=1)
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
                    raise poker_component.UnexpectedError
                if player.money == 0 and player.state != 6:
                    print(f"{player.name} broke!")
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
                raise poker_component.UnexpectedError
            if player.money == 0 and player.state != 6:
                print(f"{player.name} broke!")
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
            print(f"{player.name} wins the table! ")
            with open("poker_ai/ai/ml/default_data.json", 'w') as file:
                json.dump(datas_all, file)
                file.close()
            return player.name
        
def game_loop_model_test(num_players, init_money, n, model_list):
    STOP=1
    hehehe=0
    players, engine = game_init(num_players, init_money)
    win_dict={player.name:0 for player in players}
    tables = engine.tables
    while hehehe<n:
        players = []
        for x in range(num_players):
            players.append(poker_component.Player(
                None, f"Player {x+1}", init_money))
            players[-1].model = model_list[x]
        bext.clear()
        bext.title("Bruh poker game")
        print(tables[players[0].name].count)
        indicator=2
        count = 1
        playing = num_players
        table_condition = True
        big_blind = num_players-1
        small_blind = num_players-2
        temp_board_money = 0
        while table_condition:
            players,engine = refresh(players,engine)
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
            print_board(players, board)
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
                    print_board(players, board)
                elif k == 1:
                    board.hand.add_card(a.deal_cards())
                    board.hand.add_card(a.deal_cards())
                    board.hand.add_card(a.deal_cards())
                    print_board(players, board)
                conditioner = True
                index = (big_blind+1) % num_players
                while conditioner:
                    if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                        conditioner = False
                        break
                    if players[index].state in [-1, 1, 2]:
                        cur_call, last_raised, board.money, cur_raise = action(
                            index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, k)
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
                        raise poker_component.UnexpectedError
                    if player.money == 0 and player.state != 6:
                        print(f"{player.name} broke!")
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
            tables = table_record(tables, gamelogger.history, gamelogger.checkout, players, num_players, board)
            for player in players:
                tables[player.name] = table_rescaling(tables[player.name], len(gamelogger.history))
            for player in players:
                tables[player.name].data_observation, tables[player.name].data_action = preprocess_table(tables[player.name])
            for player in players:
                if player.money < 0:
                    raise poker_component.UnexpectedError
                if player.money == 0 and player.state != 6:
                    print(f"{player.name} broke")
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
                print(f"{player.name} wins the table!")  
                win_dict[player.name]+=1
        hehehe+=1      
    print(win_dict)

def game_loop(num_players, init_money):
    play_flag = True
    players, engine = game_init(num_players, init_money)
    tables = engine.tables
    while play_flag:
        players = []
        for x in range(num_players):
            players.append(poker_component.Player(
                None, f"Player {x+1}", init_money))
        bext.clear()
        bext.title("Bruh poker game")
        indicator = INDICATOR
        count = 1
        playing = num_players
        table_condition = True
        big_blind = num_players-1
        small_blind = num_players-2
        temp_board_money = 0
        while table_condition:
            players,engine = refresh(players,engine)
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
                            index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, engine, k)
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
                        raise poker_component.UnexpectedError
                    if player.money == 0 and player.state != 6:
                        print(f"{player.name} broke!")
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
            tables = table_record(tables, gamelogger.history, gamelogger.checkout, players, num_players, board)
            for player in players:
                tables[player.name] = table_rescaling(tables[player.name], len(gamelogger.history))
            for player in players:
                tables[player.name].data_observation, tables[player.name].data_action = preprocess_table(tables[player.name])
            for player in players:
                if player.money < 0:
                    raise poker_component.UnexpectedError
                if player.money == 0 and player.state != 6:
                    print(f"{player.name} broke!")
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
                print(f"{player.name} wins the table!")        

def game_init(num_players, init_money) -> tuple[list[poker_component.Player], OM_engine]:
    players = []
    engine = OM_engine()
    tables = engine.tables
    for x in range(num_players):
        players.append(poker_component.Player(
            None, f"Player {x+1}", init_money))
        tables[players[-1].name] = Data_table()
    try:
        f = open("poker_ai/ai/ml/default_data.json")
    except:
        raise Exception('no default data')
    else:
        datas_all = json.load(f)
        match num_players:
            case 2:
                datas = datas_all['2']
            case 3:
                datas = datas_all['4']
            case 4:
                datas = datas_all['4']
            case 5:
                datas = datas_all['6']
            case 6:
                datas = datas_all['6']
            case _:
                raise Exception('too many players')
        for player in players:
            tables[player.name].counting_table = datas.copy()
            table_rescaling(tables[player.name], 0)
            tables[player.name].count = table_counting(tables[player.name].counting_table)
            tables[player.name].data_observation, tables[player.name].data_action = preprocess_table(tables[player.name])
        f.close()
    return players,engine

def refresh(players,engine):
    for player in players:
        player.weighted_dict = {}
    return players, engine
