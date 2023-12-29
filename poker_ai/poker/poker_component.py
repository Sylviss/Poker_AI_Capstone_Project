import random
from poker_ai.constant import MODEL
from colorama import Fore, Back, Style 

class UAreStupidIfThisShowsUp(Exception):
    """A Exception class to make anyone in development team who see this embarrasing of themself
    """
    
class UnexpectedError(Exception):
    """To catch negative money glitch.
    """
class Card:

    rank_names = [None, '2', '3', '4', '5', '6', '7',
                  '8', '9', '10', 'Jack', 'Queen', 'King', "Ace"]
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

    def __init__(self, rank=2, suit=0):
        self.rank = rank
        self.suit = suit

    def printcard(self):
        rank_names = [None, '2', '3', '4', '5', '6',
                      '7', '8', '9', '10', 'J', 'Q', 'K', "A"]
        suit_names = [chr(9827), chr(9830), chr(9829), chr(9824)]
        
        color_dict = {i: Fore.BLACK if i in {chr(9827), chr(9824)} else Fore.RED for i in suit_names}
        
        row2 = Back.WHITE + color_dict[suit_names[self.suit]] + f'  {suit_names[self.suit]}  ' + Style.RESET_ALL
        
        if self.rank == 9:
            row1 = Back.WHITE + color_dict[suit_names[self.suit]] + f'{"10"}   ' + Style.RESET_ALL
            row3 = Back.WHITE + color_dict[suit_names[self.suit]] + f'   {"10"}' + Style.RESET_ALL 
            
        else:
            row1 = Back.WHITE + color_dict[suit_names[self.suit]] + f'{rank_names[self.rank]}    ' + Style.RESET_ALL
            row3 = Back.WHITE + color_dict[suit_names[self.suit]] + f'    {rank_names[self.rank]}' + Style.RESET_ALL 
            
        return [row1, row2, row3]

    def printcardsimple(self):
        rank_names = [None, '2', '3', '4', '5', '6',
                      '7', '8', '9', '10', 'J', 'Q', 'K', "A"]
        suit_names = ["c","d","h","s"]
        return rank_names[self.rank]+suit_names[self.suit]
    
    def __str__(self):
        return "\n".join(self.printcard())

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    def __lt__(self, other):
        return self.rank + self.suit*13<other.rank + other.suit*13
class Deck:

    def __init__(self, num=1):
        self.cards = []
        for _ in range(num):
            for b in range(4):
                for a in range(1, 14):
                    self.cards.append(Card(a, b))
        self.shuffle()

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card) + '\n')
        return '\n'.join(res)

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)

    def deal_cards(self):
        return self.cards.pop(0)

    def shuffle(self):
        random.shuffle(self.cards)

    def sort(self):
        self.cards.sort()

    def move_card(self, hand, num):
        '''Move {num} cards to {hand}.'''
        for _ in range(num):
            hand.add_card(self.deal_cards())

    def deal_hands(self, numhand, numcard):
        """Deal {numcard} cards to {numhand} hands

        Args:
            numhand (int): number of hand
            numcard (int): number of card

        Returns:
            list(Hand()): return a list of hands
        """
        hands_list = []
        if numcard*numhand > len(self.cards):
            print('Go get some math, noobs')
            return 0
        for _ in range(numhand):
            a = Hand()
            self.move_card(a, numcard)
            hands_list.append(a)
        return hands_list

class Player:

    def __init__(self, hand, name, money, state=-1, model=MODEL):
        self.name = name
        self.hand = hand
        self.money = money
        self.state = state
        self.pot = 0
        self.model = model
        """
        + State explain:
        -1: Initial state
        0: All-in
        1: Called/Checked 
        2: Raised
        3: Broke
        4: Fold
        5: Out of game
        6: Out of table
        + model: AI model, default is -1 (human)
        """
        # Used for storing mcts data
        self.root_node_tree=None
        self.mcts_tree=None
        # Used for storing enumerating data
        self.weighted_dict={}
        self.opponent_prob_dict={}
        self.opponent_can_act={}
        self.opponent_ingame={}
        # Used for storing machine learning data
        self.ml_data=None
        self.data_table = {}

    def __str__(self):
        hand = self.hand.printhand()
        return f"{self.name}: {self.money}$\n" + hand + "\n"


    def all_in_1(self, cur_call, last_raised, board_pot, cur_raise):
        self.pot += self.money
        board_pot += self.money
        print(f"{self.name} all in for {self.money}$")
        self.money = 0
        self.state = 0
        return (cur_call, last_raised, board_pot, cur_raise)

    def all_in_2(self, cur_call, last_raised, board_pot, cur_raise):
        cur_raise = self.money+self.pot-cur_call
        cur_call = cur_call+cur_raise
        self.pot += self.money
        board_pot += self.money
        print(f"{self.name} all in for {self.money}$")
        self.money = 0
        self.state = 0
        last_raised = self.name
        return (cur_call, last_raised, board_pot, cur_raise)

    def check(self, cur_call, last_raised, board_pot, cur_raise):
        self.state = 1
        print(f"{self.name} check")
        return (cur_call, last_raised, board_pot, cur_raise)

    def call(self, cur_call, last_raised, board_pot, cur_raise):
        self.state = 1
        bet_money = cur_call-self.pot
        self.money -= bet_money
        self.pot = cur_call
        board_pot += bet_money
        print(f"{self.name} call")
        return (cur_call, last_raised, board_pot, cur_raise)

    def raise_money(self, money_raised, cur_call, last_raised, board_pot, cur_raise):
        self.state = 2
        bet_money = cur_call-self.pot+money_raised
        cur_raise = money_raised
        cur_call += cur_raise
        print(f"{self.name} raise for {cur_raise}$")
        self.money -= bet_money
        self.pot += bet_money
        board_pot += bet_money
        last_raised = self.name
        return (cur_call, last_raised, board_pot, cur_raise)

    def fold(self, cur_call, last_raised, board_pot, cur_raise):
        self.state = 4
        print(f"{self.name} fold")
        return (cur_call, last_raised, board_pot, cur_raise)
    
class Hand(Deck):

    def __init__(self):
        self.cards = []

    def join_hands(self, hand):
        self.cards += hand.cards

    def create_poker(self, board):
        a = Poker()
        a.cards += self.cards+board.cards
        return a

    def printhand(self):
        res = ['', '', '', '']
        for card in self.cards:
            tmp = card.printcard()
            for i in range(3):
                res[i] += tmp[i] + ' '
        return '\n'.join(res)
    
    def printhandsimple(self):
        res=[]
        for card in self.cards:
            res.append(card.printcardsimple())
        return ' '.join(res)
    
    def hand_to_str(self):
        return " ".join([card_to_str(card) for card in self.cards])

    def starting_hand_str(self):
        rank_names = [None, '2', '3', '4', '5', '6',
                      '7', '8', '9', '10', 'J', 'Q', 'K', "A"]
        if len(self.cards) != 2:
            raise Exception('Not a starting hand!')
        c1 = self.cards[0].printcardsimple()
        c2 = self.cards[1].printcardsimple()
        if c1[:-1] == c2[:-1]:
            w = c1[:-1]+c2[:-1]
            return w.replace('10','T')
        elif rank_names.index(c1[:-1]) > rank_names.index(c2[:-1]):
            w = c1[:-1] + c2[:-1]
        elif rank_names.index(c1[:-1]) < rank_names.index(c2[:-1]):
            w = c2[:-1] + c1[:-1]
        if c1[-1] == c2[-1]:
            w += 's'
        else:
            w += 'o'
        return w

class Poker(Hand):

    def __init__(self):
        self.cards = []
        self.handvalue_dict = {1: 'High card', 2: 'One pair', 3: 'Two pairs', 4: 'Three of a kind',
                         5: "Straight", 6: 'Flush', 7: 'Full house', 8: 'Four of a kind', 9: 'Straight flush'}

    def create_rank_dict(self):
        '''return a {rank: number of cards have that rank} dict'''
        rank_dict = {}
        for x in self.cards:
            rank_dict[x.rank] = rank_dict.get(x.rank, 0) + 1
        return rank_dict

    def create_suit_dict(self):
        '''same as create_rank_dict but with suit'''
        suit_dict = {}
        for x in self.cards:
            suit_dict[x.suit] = suit_dict.get(x.suit, 0) + 1
        return suit_dict

    def all_multiple(self):
        '''check for multiple in hand'''
        rank_dict = self.create_rank_dict()
        num_of_mul_dict = {}
        check_final = 1 # 'value' of current hand, default == 1: high card

        # count number of multiples
        for x in rank_dict:
            num_of_mul_dict[rank_dict[x]] = num_of_mul_dict.get(rank_dict[x], 0) + 1
        for x in range(5):
            num_of_mul_dict[x] = num_of_mul_dict.get(x, 0)

        # determine the 'value' of hand
        if num_of_mul_dict[4] > 0:
            check_final = 8
        elif (num_of_mul_dict[3] > 0 and num_of_mul_dict[2] > 0) or (num_of_mul_dict[3] > 1):
            check_final = 7
        elif num_of_mul_dict[3] > 0:
            check_final = 4
        elif num_of_mul_dict[2] > 1:
            check_final = 3
        elif num_of_mul_dict[2] > 0:
            check_final = 2

        # return the highest-value multiple hand combination
        if check_final == 8:
            for x in rank_dict:
                card_4 = 0
                card_high = []
                for x in range(13, 0, -1):
                    if x in rank_dict:
                        if rank_dict[x] == 4:
                            card_4 = x
                        else:
                            card_high.append(x)
                return (8, card_4, card_high[0])
            
        elif check_final == 7:
            card_3 = 0
            card_2 = 0
            taken_card_3 = 0
            for x in range(13, 0, -1):
                if x in rank_dict:
                    if rank_dict[x] == 3 and not taken_card_3:
                        card_3 = x
                        taken_card_3 = 1
                    elif rank_dict[x] >= 2 and card_2 == 0:
                        card_2 = x
            return (7, card_3, card_2)
        
        elif check_final == 4:
            card_3 = 0
            card_high = []
            for x in range(13, 0, -1):
                if x in rank_dict:
                    if rank_dict[x] == 3:
                        card_3 = x
                    else:
                        card_high += [x]*rank_dict[x]
            return (4, card_3, card_high[0], card_high[1])
        
        elif check_final == 3:
            card_2 = []
            card_high = []
            for x in range(13, 0, -1):
                if x in rank_dict:
                    if rank_dict[x] == 2:
                        card_2 += [x]
                    else:
                        card_high += [x]
            if len(card_2) == 3 and card_2[2] > card_high[0]:
                return (3, card_2[0], card_2[1], card_2[2])
            else:
                return (3, card_2[0], card_2[1], card_high[0])
        
        elif check_final == 2:
            card_2 = 0
            card_high = []
            for x in range(13, 0, -1):
                if x in rank_dict:
                    if rank_dict[x] == 2:
                        card_2 = x
                    else:
                        card_high += [x]
            return (2, card_2, card_high[0], card_high[1], card_high[2])
        
        else:
            card_high = []
            for x in range(13, 0, -1):
                if x in rank_dict:
                    card_high += [x]
            return (1, card_high[0], card_high[1], card_high[2], card_high[3], card_high[4])

    def flush(self):
        '''check for flush in hand'''
        suit_dict = self.create_suit_dict()
        check_flush = False
        flush_suit = 0
        for x in range(4):
            suit_dict[x] = suit_dict.get(x, 0)
            if suit_dict[x] >= 5:
                check_flush = True
                flush_suit = x
        cache = []
        for card in self.cards:
            if card.suit == flush_suit:
                cache.append(card.rank)
        cache.sort(reverse=True)
        if check_flush:
            return (6, cache[0], cache[1], cache[2], cache[3], cache[4])
        return (0, 0)

    def straight(self):
        '''check for straight in hand'''
        rank_dict = self.create_rank_dict()
        rank_dict[0] = rank_dict.get(13, 0) # remainder: 13 == ace
        highest = 0
        check_flush = 0
        consecutive_count = 0
        
        for x in range(14):
            if x in rank_dict and rank_dict[x] != 0:
                consecutive_count += 1
            else:
                consecutive_count = 0
            if consecutive_count >= 5:
                check_flush = 1
                highest = x

        if check_flush == 1:
            return (5, highest)
        return (0, 0)

    def clone(self):
        '''create a clone of self'''
        temp_clone = Poker()
        temp_clone.cards = self.cards[:]
        return temp_clone

    def straight_flush(self):
        '''check for straight flush in hand'''
        if self.flush()[0] == 6:
            suit_dict = self.create_suit_dict()

            # x: the suit that has 5 or more cards
            for x in range(4):
                suit_dict[x] = suit_dict.get(x, 0)
                if suit_dict[x] >= 5:
                    break
            
            # temp: all the remaining card that has the same suit
            temp = self.clone()
            for a in temp.cards:
                if a.suit != x:
                    temp.remove_card(a)

            check_straight = temp.straight()
            if check_straight[0] == 5:
                return (9, check_straight[1])
        return (0, 0)

    def check(self):
        '''return the best value of the hand'''
        a, b, c, d = self.straight(), self.straight_flush(), self.flush(), self.all_multiple()
        values = [a, b, c, d]
        x = max(a[0], b[0], c[0], d[0])
        for k in values:
            if k[0] == x:
                return k

    def take_str_check(self):  # take the name of the hand's value
        return self.handvalue_dict[self.check()[0]]
    
rank_dicts={"A":13,"2":1,"3":2,"4":3,"5":4,"6":5,"7":6,"8":7,"9":8,"10":9,"J":10,"Q":11,"K":12}
suit_dicts={'c':0, 'd':1, 'h':2, 's':3}
reverse_rank_dicts = {v: k for k, v in rank_dicts.items()}
reverse_suit_dicts = {v: k for k, v in suit_dicts.items()}

def str_to_card(s):
    """Return a Card object base on a string

    Args:
        s (str): string representation of the card

    Returns:
        Card: card object of the card
    """
    suit=s[::-1][0]
    rank=s[:-1]
    return Card(rank_dicts[rank],suit_dicts[suit])

def card_to_str(card):
    """Return a Card object base on a string

    Args:
        card(Card): card object of the card

    Returns:
        String: string representation of the card
    """
    rank = reverse_rank_dicts[card.rank]
    suit = reverse_suit_dicts[card.suit]
    return rank + suit

def int_to_card(a):
    if a%13==0:
        suit=a//13-1
        rank=13
    else:
        rank=a%13
        suit=a//13
    return Card(rank,suit)

class Gamelogger:
    def __init__(self,players):
        """Explain for keylogging:
        There are much more stage than normal, because raise 1$ and all in are much different. The action can be changed into different case like this:
        1: All in -  8: All in
        2: Check -   1: Check
        3: Call: depend on the money
        we have 2 stages for call
                     2: Call min-med
                     3: Call high
        4: Raise: depend on the money
        we have 3 stages for raise:
                     4: Raise min
                     5: Raise med
                     6: Raise high
        5: Fold  -   7: Fold
        6: Raise max
        this is the same as raise, as raise max for one people is just a little bit of money, when with others it's their whole stash.
        """
        self.raised_time=0
        self.history=[]
        self.action_history={player.name:0 for player in players if player.state!=6}
        self.money_history=[]
        self.action_count=0
        self.raise_number=0
        self.cur_turn=-1   
        self.checkout = []
        
    def next_turn(self):
        match self.cur_turn:
            case -1:
                self.cur_turn=0
            case 0:
                self.cur_turn=3
            case 3:
                self.cur_turn=4
            case 4:
                self.cur_turn=5
            case _:
                raise UnexpectedError
        self.raise_number=0
        self.raised_time=0
        
    def keylogging(self, player, action, checkout):
        self.action_history[player.name]=self.cur_turn
        self.action_count+=1
        money=0
        match action[0]:
            case 1:
                action_logged=8
            case 2:
                action_logged=1
            case 3:
                ratio=action[1]
                if ratio<0.2:
                    action_logged=2
                else:
                    action_logged=3
            case 4:
                ratio=action[1]
                money=action[2]
                match self.raise_number:
                    case 0:
                        if ratio<0.2:
                            action_logged=4
                        elif ratio<0.4:
                            action_logged=5
                        else:
                            action_logged=6
                    case 1:
                        if ratio<0.4:
                            action_logged=5
                        else:
                            action_logged=6
                    case 2:
                        if ratio<0.4:
                            action_logged=5
                        else:
                            action_logged=6
                    case _:
                        action_logged=6
                self.raise_number+=1
                self.raised_time+=1
            case 5:
                action_logged=7
            case 6:
                ratio=action[1]
                money=action[2]
                match self.raise_number:
                    case 0:
                        if ratio<0.3:
                            action_logged=4
                        elif ratio<0.5:
                            action_logged=5
                        else:
                            action_logged=6
                    case 1:
                        if ratio<0.3:
                            action_logged=5
                        else:
                            action_logged=6
                    case _:
                        action_logged=6
                self.raise_number+=1
                self.raised_time+=1
            case _:
                raise UnexpectedError
        self.history.append((player.name,self.cur_turn,action_logged))
        self.money_history.append(money)
        self.checkout.append((player.name, checkout.copy()))
