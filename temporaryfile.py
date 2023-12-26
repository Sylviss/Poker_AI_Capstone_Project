import bext, json
from poker_ai.poker import poker_component
from poker_ai.ai.ai_algorithm import action_ai_model
from poker_ai.ai.ai_algorithm_om import action_ai_with_om_model
from poker_ai.constant import STOP, PREFLOP_BIG_BLIND, INDICATOR, MULTIPROCESS, TURN_TO_RAISE_POT, DEBUG_MODE
from poker_ai.ai.ml.opponent_modelling import Data_table, magical_four, preprocess_table, recording, table_counting, table_record, table_rescaling
from poker_ai.ai.ml.methods import OM_engine

from poker_ai.tools import *
# blockPrint()

import pygame
import os, sys
from poker_ai.poker.poker_component import reverse_suit_dicts
from poker_ai.poker.play import *


HEIGHT = 720
WIDTH = 1280

BLACK = (255, 255, 255)
BLACK = (0, 0, 0)
GREY  = (50, 50, 50)
RED  = (207, 0, 0)




def card_to_img_path(card: 'poker_component.Card') -> str:
    return f'res/img/{card.rank + 1}{reverse_suit_dicts[card.suit].upper()}.png'





def game_loop(num_players, init_money):
    play_flag = True
    players, engine = game_init(num_players, init_money)
    tables = engine.tables
    while play_flag:
        players = []
        for x in range(num_players):
            players.append(poker_component.Player(
                None, f"Player {x+1}", init_money))
        # bext.clear()
        # bext.title("Bruh poker game")
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
                # bext.clear()
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
            # bext.clear()
        for player in players:
            if player.state != 6:
                print(f"{player.name} wins the table!")

