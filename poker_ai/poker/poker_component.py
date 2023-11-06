import random


class UAreStupidIfThisShowsUp(Exception):
    """A Exception class to make anyone who see this embarrasing of themself
    """
    
class WTF(Exception):
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
        ceiling = ' ___ '
        row2 = f'| {suit_names[self.suit]} |'
        if self.rank == 9:
            row1 = '|10 |'
            row3 = '|_10|'
        else:
            row1 = f'|{rank_names[self.rank]}  |'
            row3 = f'|__{rank_names[self.rank]}|'
        return [ceiling, row1, row2, row3]

    def __str__(self):
        return "\n".join(self.printcard())

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


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
            res.append(str(card))
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

    def __init__(self, hand, name, money, state=-1):
        self.name = name
        self.hand = hand
        self.money = money
        self.state = state
        self.pot = 0
        """
        + State explain:
        -1: Initial state
        0: All-in
        1: Called/Checked 
        2: Raised
        3: Broke as fuck
        4: Fold
        5: Out of game
        6: Out of table
        """

    def __str__(self):
        hand = self.hand.printhand()
        return f"{self.name}: {self.money}$\n" + hand + "\n"

    def action_human(self, cur_call, last_raised, board_pot, cur_raise):
        """
            types of number:
            1.1: All-in 1: Avalable if self.money <= cur_call-self.pot
            1.2. All-in 2: Avalable if self.money > cur_call-self.pot
            2. Check: Avalable if cur_call == self.pot
            3. Call: Avalable if cur_call > self.pot
            4. Raise: Avalable if self.money > cur_call-self.pot+cur_raise. Must raise at least cur_raise and max almost all in.
            5. Fold: whenever you want it

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

        # hehe = ", ".join(stack)

        print(f"{self.name} need to put in at least {cur_call-self.pot}$")

        # print(f"Choose between {hehe}")
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
            if self.money <= cur_call-self.pot:
                ans = self.all_in_1(cur_call, last_raised,
                                    board_pot, cur_raise)
            else:
                ans = self.all_in_2(cur_call, last_raised,
                                    board_pot, cur_raise)
                
        elif action == 2:
            ans = self.check(cur_call, last_raised, board_pot, cur_raise)

        elif action == 3:
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
                break

        elif action == 5:
            ans = self.fold(cur_call, last_raised, board_pot, cur_raise)
        return ans


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
            for i in range(4):
                res[i] += tmp[i] + ' '
        return '\n'.join(res)


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