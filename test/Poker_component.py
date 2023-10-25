import random

class UAreStupidIfThisShowsUp(Exception):
    pass
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
        for _ in range(num):
            for b in range(4):
                for a in range(1,14):
                    self.cards.append(Card(a,b))
        self.shuffle()
        
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

class Player:
    
    def __init__(self,hand,name,money,state=-1):
        self.name=name
        self.hand=hand
        self.money=money
        self.state=state
        self.pot=0
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
        + Money flow:
        - In-turn: money->self.pot
        - After bet turn: self.pot->boardpot
        """    
    def __str__(self):
        return f"{self.name}: {self.money}$\n" + str(self.hand) + "\n"
    
    def action(self,indicator,cur_call,last_raised,board_pot,cur_raise):
        if indicator==0:
            return self.action_human(cur_call,last_raised,board_pot,cur_raise)
        elif indicator==1:
            if self.name=="Player 1":
                return self.action_human(cur_call,last_raised,board_pot,cur_raise)
            return self.action_randombot(cur_call,last_raised,board_pot,cur_raise)
        else:
            return self.action_randombot(cur_call,last_raised,board_pot,cur_raise)
    
    def action_randombot(self,cur_call,last_raised,board_pot,cur_raise):
        checkout=[1,5,5]
        if cur_call==self.pot:
            for _ in range(4):
                checkout.append(2)
        elif cur_call>self.pot and self.money>cur_call-self.pot:
            for _ in range(4):
                checkout.append(3)
        if self.money>cur_call-self.pot+cur_raise:
            for _ in range(2):
                checkout.append(4)
        print(f"{self.name} need to put in at least {cur_call-self.pot}$")
        a=random.choice(checkout)
        print(f"Bot choose {a}")
        if a==1:
            if self.money<=cur_call-self.pot:
                ans=self.all_in_1(cur_call,last_raised,board_pot,cur_raise)
            else:
                ans=self.all_in_2(cur_call,last_raised,board_pot,cur_raise)
        elif a==2:
            ans=self.check(cur_call,last_raised,board_pot,cur_raise)
        elif a==3:
            ans=self.call(cur_call,last_raised,board_pot,cur_raise)
        elif a==4:
            b=random.randint(cur_raise,self.money-1-(cur_call-self.pot))
            ans=self.raise_money(b,cur_call,last_raised,board_pot,cur_raise)
        elif a==5:
            ans=self.fold(cur_call,last_raised,board_pot,cur_raise)
        return ans
    
    def action_human(self,cur_call,last_raised,board_pot,cur_raise):
        """_summary_
            types of number:
            1.1: All-in 1: Avalable if self.money<=cur_call-self.pot
            1.2. All-in 2: Avalable if self.money>cur_call-self.pot
            2. Check: Avalable if cur_call==self.pot
            3. Call: Avalable if cur_call>self.pot
            4. Raise: Avalable if self.money>cur_call-self.pot+cur_raise. Must raise at least cur_raise and max almost all in.
            5. Fold: whenever you want it
        """
        checkout=[1,5]
        stack=["fold","all in"]
        if cur_call==self.pot:
            stack.append("check")
            checkout.append(2)
        elif cur_call>self.pot and self.money>cur_call-self.pot:
            stack.append("call")
            checkout.append(3)
        if self.money>cur_call-self.pot+cur_raise:
            stack.append("raise")
            checkout.append(4)
        hehe=", ".join(stack)
        print(f"{self.name} need to put in at least {cur_call-self.pot}$")
        print(f"Choose between {hehe}")
        print("1: all in, 2: check, 3: call, 4: raise, 5: fold")
        a=int(input())
        if a not in checkout:
            raise UAreStupidIfThisShowsUp
        if a==1:
            if self.money<=cur_call-self.pot:
                ans=self.all_in_1(cur_call,last_raised,board_pot,cur_raise)
            else:
                ans=self.all_in_2(cur_call,last_raised,board_pot,cur_raise)
        elif a==2:
            ans=self.check(cur_call,last_raised,board_pot,cur_raise)
        elif a==3:
            ans=self.call(cur_call,last_raised,board_pot,cur_raise)
        elif a==4:
            print(f"Please choose between {cur_raise}$ and {self.money-1-(cur_call-self.pot)}$")
            b=int(input())
            ans=self.raise_money(b,cur_call,last_raised,board_pot,cur_raise)
        elif a==5:
            ans=self.fold(cur_call,last_raised,board_pot,cur_raise)
        return ans
    def all_in_1(self,cur_call,last_raised,board_pot,cur_raise):
        self.pot+=self.money
        board_pot+=self.money
        print(f"{self.name} all in for {self.money}$")
        self.money=0
        self.state=0
        return (cur_call,last_raised,board_pot,cur_raise)

    def all_in_2(self,cur_call,last_raised,board_pot,cur_raise):
        cur_raise=self.money+self.pot-cur_call
        cur_call=cur_call+cur_raise
        self.pot+=self.money
        board_pot+=self.money
        print(f"{self.name} all in for {self.money}$")
        self.money=0
        self.state=0
        last_raised=self.name
        return (cur_call,last_raised,board_pot,cur_raise)
    
    def check(self,cur_call,last_raised,board_pot,cur_raise):
        self.state=1
        print(f"{self.name} check")
        return (cur_call,last_raised,board_pot,cur_raise)
    
    def call(self,cur_call,last_raised,board_pot,cur_raise):
        self.state=1
        bet_money=cur_call-self.pot
        self.money-=bet_money
        self.pot=cur_call
        board_pot+=bet_money
        print(f"{self.name} call")
        return (cur_call,last_raised,board_pot,cur_raise)
    
    def raise_money(self,money_raised,cur_call,last_raised,board_pot,cur_raise):
        self.state=2
        bet_money=cur_call-self.pot+money_raised
        cur_raise=money_raised
        cur_call+=cur_raise
        print(f"{self.name} raise for {cur_raise}$")
        self.money-=bet_money
        self.pot+=bet_money
        board_pot+=bet_money
        last_raised=self.name
        return (cur_call,last_raised,board_pot,cur_raise)
    
    def fold(self,cur_call,last_raised,board_pot,cur_raise):
        self.state=4
        print(f"{self.name} fold")
        return (cur_call,last_raised,board_pot,cur_raise)
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

    def createdict(self): #return a rank -> number of cards have that rank dict
        dictbruh={}
        for x in self.cards:
            dictbruh[x.rank]=dictbruh.get(x.rank,0)+1
        return dictbruh

    def createdictbruh(self): #same as before but with suit
        dictbruh={}
        for x in self.cards:
            dictbruh[x.suit]=dictbruh.get(x.suit,0)+1
        return dictbruh

    def all_multiple(self):
        dictbruh=self.createdict()
        bruhbruhbruh={}
        check_final=1
        for x in dictbruh:
            bruhbruhbruh[dictbruh[x]]=bruhbruhbruh.get(dictbruh[x],0)+1
        for x in range(5):
            bruhbruhbruh[x] = bruhbruhbruh.get(x,0)
        if bruhbruhbruh[4]>0:
            check_final=8
        elif (bruhbruhbruh[3]>0 and bruhbruhbruh[2]>0) or (bruhbruhbruh[3]>1):
            check_final=7
        elif bruhbruhbruh[3]>0:
            check_final=4
        elif bruhbruhbruh[2]>1:
            check_final=3
        elif bruhbruhbruh[2]>0:
            check_final=2
        if check_final==8:
            for x in dictbruh:
                card_4=0
                card_high=[]
                for x in range(13,0,-1):
                    if x in dictbruh:
                        if dictbruh[x]==4:
                            card_4=x
                        else:
                            card_high.append(x)
                return (8,card_4,card_high)
        elif check_final==7:
            card_3=0
            card_2=0
            taken_card_3=0
            for x in range(13,0,-1):
                if x in dictbruh:
                    if dictbruh[x]==3 and not taken_card_3:
                        card_3=x
                        taken_card_3=1
                    elif dictbruh[x]>=2 and card_2==0:
                        card_2=x
            return (7,card_3,card_2)
        elif check_final==4:
            card_3=0
            arr=[]
            for x in range(13,0,-1):
                if x in dictbruh:
                    if dictbruh[x]==3:
                        card_3=x
                    else:
                        arr+=[x]*dictbruh[x]
            return (4,card_3,arr[0],arr[1])
        elif check_final==3:
            card_2=[]
            card_high=[]
            for x in range(13,0,-1):
                if x in dictbruh:
                    if dictbruh[x]==2:
                        card_2+=[x]
                    else:
                        card_high+=[x]
            if len(card_2)==3 and card_2[2]>card_high[0]:
                return (3,card_2[0],card_2[1],card_2[2])
            else:
                return (3,card_2[0],card_2[1],card_high[0])
        elif check_final==2:
            card_2=0
            card_high=[]
            for x in range(13,0,-1):
                if x in dictbruh:
                    if dictbruh[x]==2:
                        card_2=x
                    else:
                        card_high+=[x]
            return (2,card_2,card_high[0],card_high[1],card_high[3])
        else:
            card_high=[]
            for x in range(13,0,-1):
                if x in dictbruh:
                    card_high+=[x]
            return (1,card_high[0],card_high[1],card_high[2],card_high[3],card_high[4])
        
    def flush(self):
        dictbruh=self.createdictbruh()
        ans_flush=0
        temp=0
        for x in range(4):
            dictbruh[x]=dictbruh.get(x,0)
            if dictbruh[x]>=5:
                ans_flush=6
                temp=x
        cache=[]
        for card in self.cards:
            if card.suit==temp:
                cache.append(card.rank)
        cache.sort()
        if ans_flush==6:
            return (6,cache[0],cache[1],cache[2],cache[3],cache[4])
        return (0,0)
    
    def straight(self):
        dictbruh=self.createdict()
        dictbruh[14]=dictbruh.get(1,0)
        highest=0
        check_flush=0
        k=0
        for x in range(1,15):
            if x in dictbruh and dictbruh[x]!=0:
                k+=1
            else:
                k=0
            if k==5:
                check_flush=1
                highest=x
        if check_flush==1:
            return (5,highest)
        return (0,0)

    def straight_flush(self):
        if self.flush()[0]==6:
            dictbruh=self.createdictbruh()
            for x in range(4):
                dictbruh[x]=dictbruh.get(x,0)
                if dictbruh[x]>=5:
                    break
            for a in self.cards:
                if a.suit!=x:
                    self.remove_card(a)
            check_straight=self.straight()
            if check_straight[0]==5:
                return (9,check_straight[1])
        return (0,0)


    def check(self):
        a,b,c,d=self.straight(),self.straight_flush(),self.flush(),self.all_multiple()
        hehe=[a,b,c,d]
        x=max(a[0],b[0],c[0],d[0])
        for k in hehe:
            if k[0]==x:
                return k

    def take_str_check(self,a):
        return self.dicthaha[a] 
