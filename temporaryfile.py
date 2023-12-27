import bext, json
import math
from poker_ai.poker import poker_component
# from poker_ai.ai.ai_algorithm import action_ai_model
# from poker_ai.ai.ai_algorithm_om import action_ai_with_om_model
# from poker_ai.constant import STOP, PREFLOP_BIG_BLIND, INDICATOR, MULTIPROCESS, TURN_TO_RAISE_POT, DEBUG_MODE
# from poker_ai.ai.ml.opponent_modelling import Data_table, magical_four, preprocess_table, recording, table_counting, table_record, table_rescaling
# from poker_ai.ai.ml.methods import OM_engine

from poker_ai.tools import *
blockPrint()


import pygame
pygame.init()
import os, sys
from poker_ai.poker.poker_component import reverse_suit_dicts
from poker_ai.poker.play import *

NUM_COMMUNITY = {0: 0, 1: 3, 2: 4, 3: 5}


HEIGHT = 720
WIDTH = 1280

# HEIGHT = 1080
# WIDTH = 1920

SCALE = 0.35
CARD_SIZE = (int(WIDTH / 7 * SCALE), int(WIDTH / 5 * SCALE))
CHIP_SIZE = (int(WIDTH / 12 * SCALE), int(WIDTH / 10 * SCALE))

SPACER = int(HEIGHT + 0.005)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY  = (50, 50, 50)
RED  = (207, 0, 0)
ORANGE = (255, 153, 51)
YELLOW = (255, 255, 0)


def player_pos(max_players: int, player: int) -> tuple[int, int]:
    return int(0.425*WIDTH - 1.6*0.35*HEIGHT*math.sin(2*math.pi*player/max_players)), HEIGHT - int(0.5*HEIGHT - 0.35*HEIGHT*math.cos(2*math.pi*player/max_players))


def card_to_img_path(r: int, s: int) -> str:
    return f'res/img/{r + 1}{reverse_suit_dicts[s].upper()}.png'

class Control:
    def __init__(self, num_players: int, init_money: int) -> None:

        self.num_players = num_players
        self.init_money = init_money

        # cards
        self.card_imgs = {}
        for r in range(1, 14):
            for s in range(4):
                self.card_imgs[(r, s)] = pygame.image.load(card_to_img_path(r, s)).convert_alpha()
                self.card_imgs[(r, s)] = pygame.transform.scale(self.card_imgs[(r, s)], (int(CARD_SIZE[0]), int(CARD_SIZE[1])))
        
        self.card_back = pygame.transform.scale(pygame.image.load('res/img/back.png'), (int(CARD_SIZE[0]), int(CARD_SIZE[1])))
        
        self.background = pygame.image.load('res/img/background3.jpg')
        self.background = pygame.transform.scale(self.background, (WIDTH*1.3, HEIGHT*1.5))
        
        self.icon = pygame.image.load('res/img/poker.png')
        pygame.display.set_icon(self.icon)
        
        self.font = pygame.font.Font('res/font/JQKWild.ttf', int(0.05 * HEIGHT))
        self.font.set_bold(True)
        
        self.font2 = pygame.font.Font('res/font/JQKWild.ttf', int(0.035 * HEIGHT))

        self.k = 10

        self.folded_state = self.font.render(f'Folded', True, GREY, WHITE)

        self.players, self.engine = game_init(num_players, init_money)
        self.tables = self.engine.tables
        
        
    
    def main(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        self.display_blind_board(1,1,1,1)

    def main2(self, num_players, init_money) -> None:
        players = []
        for x in range(num_players):
            players.append(poker_component.Player(
                None, f"Player {x+1}", init_money))
        indicator = INDICATOR
        count = 1
        playing = num_players
        table_condition = True
        big_blind = num_players-1
        small_blind = num_players-2
        temp_board_money = 0
        while table_condition:
            players,self.engine = refresh(players,self.engine)
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
            k = 0
            print_blind_board(players, board)
            self.display_blind_board(players, board, count, k)

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
                    self.display_blind_board(players, board, count, k)
                elif k == 1:
                    board.hand.add_card(a.deal_cards())
                    board.hand.add_card(a.deal_cards())
                    board.hand.add_card(a.deal_cards())
                    print_blind_board(players, board)
                    self.display_blind_board(players, board, count, k)
                conditioner = True
                index = (big_blind+1) % num_players
                while conditioner:
                    if last_raised == players[index].name and (players[index].state == 2 or players[index].state == 0):
                        conditioner = False
                        break
                    if players[index].state in [-1, 1, 2]:
                        cur_call, last_raised, board.money, cur_raise = action(
                            index, players, indicator, cur_call, last_raised, board.money, cur_raise, playing-folded, board, big_blind, preflop_big_blind_value, gamelogger, small_blind, preflop_big_blind_value, self.engine, k)
                        self.display_blind_board(players, board, count, k)
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
                    self.display_board(players, board, count, k)
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
            self.display_board(players, board, count, k)
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
            self.tables = table_record(self.tables, gamelogger.history, gamelogger.checkout, players, num_players, board)
            for player in players:
                self.tables[player.name] = table_rescaling(self.tables[player.name], len(gamelogger.history))
            for player in players:
                self.tables[player.name].data_observation, self.tables[player.name].data_action = preprocess_table(self.tables[player.name])
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


    def draw_hand(self, p: poker_component.Player, x: int, y: int) -> None:
        name_rect = self.font2.render(p.name, True, GREY, ORANGE)
        p_money_rect = self.font2.render(f'${p.money}', True, GREY, ORANGE)
        # name_rect.set_alpha(170)
        SCREEN.blit(self.card_imgs[p.hand.cards[0].rank, p.hand.cards[0].suit], (x - CARD_SIZE[0], y - CARD_SIZE[1]//2))
        SCREEN.blit(self.card_imgs[p.hand.cards[1].rank, p.hand.cards[1].suit], (x, y - CARD_SIZE[1]//2))
        pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(x + CARD_SIZE[0], y - CARD_SIZE[1]//2, name_rect.get_size()[0], name_rect.get_size()[1] + p_money_rect.get_size()[1]))
        SCREEN.blit(name_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2))
        SCREEN.blit(p_money_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2 + name_rect.get_size()[1]))

    def draw_blind_hand(self, p: poker_component.Player, x: int, y: int) -> None:
        name_rect = self.font2.render(p.name, True, GREY, ORANGE)
        p_money_rect = self.font2.render(f'${p.money}', True, GREY, ORANGE)
        # name_rect.set_alpha(170)
        SCREEN.blit(self.card_back, (x - CARD_SIZE[0], y - CARD_SIZE[1]//2))
        SCREEN.blit(self.card_back, (x, y - CARD_SIZE[1]//2))
        pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(x + CARD_SIZE[0], y - CARD_SIZE[1]//2, name_rect.get_size()[0], name_rect.get_size()[1] + p_money_rect.get_size()[1]))
        SCREEN.blit(name_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2))
        SCREEN.blit(p_money_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2 + name_rect.get_size()[1]))
    
    def draw_folded_hand(self, p: poker_component.Player, x: int, y: int) -> None:
        name_rect = self.font2.render(p.name, True, GREY, ORANGE)
        p_money_rect = self.font2.render(f'${p.money}', True, GREY, ORANGE)
        # name_rect.set_alpha(170)
        SCREEN.blit(self.folded_state, (int(x - self.font.size(f'Folded')[0] / 2), int(y - self.font.size(f'Folded')[1] / 2)))
        pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(x + CARD_SIZE[0], y - CARD_SIZE[1]//2, name_rect.get_size()[0], name_rect.get_size()[1] + p_money_rect.get_size()[1]))
        SCREEN.blit(name_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2))
        SCREEN.blit(p_money_rect, (x + CARD_SIZE[0], y - CARD_SIZE[1]//2 + name_rect.get_size()[1]))

    def draw_comm_info(self, k: int, board: poker_component.Player) -> None:
        num_comm = NUM_COMMUNITY[k]
        comm_card_pos = 0.425*WIDTH, 0.45*HEIGHT
        for i in range(num_comm):
            x, y = comm_card_pos[0] - (2.5 - i)*CARD_SIZE[0], comm_card_pos[1] - 0.5*CARD_SIZE[1]
            SCREEN.blit(self.card_imgs[board.hand.cards[i].rank, board.hand.cards[i].suit], (int(x), int(y)))
        
        ### right below the card ###
        comm_money_rect = self.font2.render(f'${board.money}', True, YELLOW)
        SCREEN.blit(comm_money_rect, (comm_card_pos[0] - comm_money_rect.get_size()[0]//2, int(comm_card_pos[1] + 0.5*CARD_SIZE[1])))


    def display_blind_board(self, players: 'list[poker_component.Player]', board: poker_component.Player, count: int, k: int) -> None:
        SCREEN.blit(self.background, (-0.22222 * WIDTH, -0.25 * HEIGHT))
        for player in range(self.num_players):
            x, y = player_pos(self.num_players, player)
            if players[player].state not in [4, 5, 6] and players[player].name == 'Player 1':
                self.draw_hand(players[player], x, y)
            elif players[player].state not in [4, 5, 6] and players[player].name != 'Player 1':
                self.draw_blind_hand(players[player], x, y)
            elif players[player].state != 6:
                self.draw_folded_hand(players[player], x, y)

        # line
        pygame.draw.rect(SCREEN, BLACK, pygame.Rect(0.85*WIDTH, 0, 0.15*WIDTH, HEIGHT), 0)
        count_rect = self.font.render(f'GAME {count}', True, (255, 0, 0))
        SCREEN.blit(count_rect, (int(0.925 * WIDTH - self.font.size(f'GAME {count}')[0] / 2), int(0.03 * HEIGHT)))

        self.draw_comm_info(k, board)
    
        pygame.display.flip()


    def display_board(self, players: 'list[poker_component.Player]', board: poker_component.Player, count: int, k: int) -> None:
        SCREEN.blit(self.background, (-0.22222 * WIDTH, -0.25 * HEIGHT))
        for player in range(self.num_players):
            x, y = player_pos(self.num_players, player)
            if players[player].state not in [4, 5, 6]:
                self.draw_hand(players[player], x, y)
            elif players[player].state != 6:
                self.draw_folded_hand(players[player], x, y)

        # line
        pygame.draw.rect(SCREEN, BLACK, pygame.Rect(0.85*WIDTH, 0, 0.15*WIDTH, HEIGHT), 0)
        count_rect = self.font.render(f'GAME {count}', True, (255, 0, 0))
        SCREEN.blit(count_rect, (int(0.925 * WIDTH - self.font.size(f'GAME {count}')[0] / 2), int(0.03 * HEIGHT)))

        self.draw_comm_info(k, board)
    
        pygame.display.flip()

class Movement:
    def __init__(self, target_x, target_y):
        chip = pygame.image.load('res/img/pkchip.png')
        self.chip = pygame.transform.scale(chip, (CHIP_SIZE[0], CHIP_SIZE[0]))
        self.target = (target_x, target_y)
        self.distance = 0
        self.N = 1000
        
    def move(self, chip_x, chip_y):
        S = math.sqrt((chip_x - self.target[0]) ** 2 + (chip_y - self.target[1]) ** 2)
        tmp1, tmp2 = chip_x, chip_y
        a, b = S / self.N, 2 * math.pi / self.N
        
    
        alpha = math.atan((chip_x - self.target[0]) / (chip_y - self.target[1]))
        
        
        running = True 
        while running:
            
            Myclock.tick(self.N)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for i in range(1, self.N + 1):
                if self.distance < S:
                    self.distance += velocity(i, a, b) 
                    chip_x = tmp1 + math.sin(alpha) * self.distance
                    chip_y = tmp2 + math.cos(alpha) * self.distance 

                    SCREEN.fill((0, 0, 0))
                    SCREEN.blit(self.chip, (chip_x, chip_y))
                    
                    pygame.display.flip()
                    
                
        pygame.quit()

def velocity(x, a, b):
    return a * (1 - math.cos(b * x))

if __name__ == "__main__":
    # os.environ['SDL_VIDEO_CENTERED'] = '1' #center screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '900, 0'
    pygame.display.set_caption("Poker")
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    
    Runit = Control(6, 500)
    Myclock = pygame.time.Clock()
    while True:
        Runit.main2(6, 500)
        Myclock.tick(60)