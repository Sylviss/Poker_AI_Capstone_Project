import random

class Card:
    
    rank_names = [None, 'Ace', '2', '3', '4', '5', '6', '7','8', '9', '10', 'Jack', 'Queen', 'King']
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

    def __init__(self, rank=2, suit=0):
        self.rank=rank
        self.suit=suit

    def __str__(self):
        return '%s of %s' % (Card.rank_names[self.rank],Card.suit_names[self.suit])

    def card_to_number(self):
        return (self.rank-1)+self.suit*13
    
    def __lt__(self,other):
        t1 = self.suit, self.rank
        t2 = other.suit, other.rank
        return t1 < t2


class Deck:

    def __init__(self,num=1):
        self.cards=[]
        self.shuffle()
        for _ in range(num):
            for b in range(4):
                for a in range(1,14):
                    self.cards.append(Card(a,b))

    def __str__(self):
        res=[]
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def add_card(self,card):
        self.cards.append(card)

    def remove_card(self,card):
        self.cards.remove(card)

    def deal_cards(self):
        return self.cards.pop(0)

    def shuffle(self):
        random.shuffle(self.cards)

    def sort(self):
        self.cards.sort()

    def move_card(self,hand,num):
        for _ in range(num):
            hand.add_card(self.deal_cards())

    def deal_hands(self,numhand,numcard):
        listbruh=[]
        if numcard*numhand>len(self.cards):
            print('Go get some math, noobs')
            return 0
        for _ in range(numhand):
            a=Hand()
            self.move_card(a,numcard)
            listbruh.append(a)
        return listbruh

class Hand(Deck):
    
    def __init__(self):
        self.cards=[]
    
    def join_hands(self,hand):
        self.cards+=hand.cards

    def create_poker(self,board):
        a=Poker()
        a.cards+=self.cards+board.cards
        return a
class Poker(Hand):

    def __init__(self):
        self.cards=[]
        self.dicthaha={1:'High card',2:'One pair',3:'Two pairs',4:'Three of a kind',5:"Straight",6:'Flush',7:'Full house',8:'Four of a kind',9:'Straight flush'}

    def createdict(self):
        dictbruh={}
        for x in self.cards:
            dictbruh[x.rank]=dictbruh.get(x.rank,0)+1
        return dictbruh

    def createdictbruh(self):
        dictbruh={}
        for x in self.cards:
            dictbruh[x.suit]=dictbruh.get(x.suit,0)+1
        return dictbruh

    def all_multiple(self):
        dictbruh=self.createdict()
        bruhbruhbruh={}
        for x in dictbruh:
            bruhbruhbruh[dictbruh[x]]=bruhbruhbruh.get(dictbruh[x],0)+1
        for x in range(5):
            bruhbruhbruh[x]=bruhbruhbruh.get(x,0)
        if bruhbruhbruh[4]>0:
            return 8
        elif bruhbruhbruh[3]>0 and bruhbruhbruh[2]>0:
            return 7
        elif bruhbruhbruh[3]>0:
            return 4
        elif bruhbruhbruh[2]>1:
            return 3
        elif bruhbruhbruh[2]>0:
            return 2
        return 1

    def flush(self):
        dictbruh=self.createdictbruh()
        for x in range(4):
            dictbruh[x]=dictbruh.get(x,0)
            if dictbruh[x]>=5:
                return 6
        return 1
    
    def straight(self):
        dictbruh=self.createdict()
        dictbruh[14]=dictbruh.get(1,0)
        k=0
        for x in range(1,15):
            if x in dictbruh and dictbruh[x]!=0:
                k+=1
            else:
                k=0
            if k==5:
                return 5
        return 1

    def straight_flush(self):
        if self.flush()==6:
            dictbruh=self.createdictbruh()
            for x in range(4):
                dictbruh[x]=dictbruh.get(x,0)
                if dictbruh[x]>=5:
                    break
            for a in self.cards:
                if a.suit!=x:
                    self.remove_card(a)
            if self.straight()==5:
                return 9
        return 1


    def check(self):
        a=max(self.straight(),self.straight_flush(),self.flush(),self.all_multiple())
        return self.dicthaha[a] 

