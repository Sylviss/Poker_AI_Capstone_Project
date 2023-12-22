from poker_ai.ai.ml.methods import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.constant import RESCALING_SIZE
from poker_ai.poker.poker_component import card_to_str
from test import check_validity
from time import time

class Data_table():
    def __init__(self):
        RANK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        SUIT = ['s', 'c', 'd', 'h']
        cards = [RANK[i]+SUIT[j] for i in range(len(RANK)) for j in range(len(SUIT))]
        hands = []
        for i in range(len(cards)-1):
            for j in range(i+1, len(cards)):
                hands.append(' '.join(sorted([cards[i],cards[j]])))
        self.counting_table = {i: {j: {k: {l:0 for l in ['fold', 'check', 'call', 'raise', 'all in']}
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for i in hands}
        self.count = 0
    def refresh_table(self):
        self.__init__()

def table_building(history, tables, hand, check_flag):
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    data = history[-1]
    counting_table = tables.counting_table
    match data[1]:
        case 0:
            counting_table[hand]['preflop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 3:
            counting_table[hand]['flop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 4:
            counting_table[hand]['turn'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 5:
            counting_table[hand]['river'][check_flag][ACTION_TABLE[data[2]]] += 1
    tables.count += 1
    return tables

def recording(tables, history, checkout, player_hand):
    if history == []:
        return '????'
    tmp = []
    for card in player_hand.cards:
        tmp.append(card_to_str(card))
    hand = ' '.join(sorted(tmp))
    if 2 in checkout and 3 not in checkout:
        check_flag = 'can only check'
    elif 2 not in checkout and 3 in checkout:
        check_flag = "can only call"
    elif 2 not in checkout and 3 not in checkout:
        check_flag = "can't check or call"
    else:
        raise Exception('wait wot???')
    tables = table_building(history, tables, hand, check_flag)
    return tables

def modelling(tables, turn, human, board, num_player, checkout):
    '''
    a function to model the type of opponent
    Input:
    -) history: Gamelogger.history
    -) tables: a dictionary contain player names mapped to their count table
    -) recorder: Rate_recorder.win
    Output:
    a tuple ({type of oppent},{list of move prob}) where:
        -) type of opponent is an int:
            +) 0: Conservative-tight
            +) 1: Conservative-loose
            +) 2: Agressive-tight
            +) 3: Agressive-loose
        -) list of move prob is a list that list all move prob
    '''

    TURN_TABLE = ['preflop','flop','turn','river']

    if 2 in checkout and 3 not in checkout:
        check_flag = 'can only check'
    elif 2 not in checkout and 3 in checkout:
        check_flag = "can only call"
    elif 2 not in checkout and 3 not in checkout:
        check_flag = "can't check or call"
    else:
        raise Exception('wait wot???')

    tmp = {i:{'phi':[None,0,0,0,0,0],\
              'po':0,\
              'po_hi':[0,0,0,0,0,0],\
             } for i in tables}
    res = {i:[0 for i in range(7)] for i in tables}

    for player in tables:
        table = tables[player].counting_table
        count = table_counting(tables[player].counting_table)
        so = 0
        so_hi = [0, 0, 0, 0, 0, 0]
        shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
        hands = {i: 0 for i in range(6)}
        some = 0
        for hand in table:
            so = 0
            so_hi = [0, 0, 0, 0, 0, 0]
            shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
            for _hand in table:
                if _hand == hand:
                    for _turn in table[_hand]:
                        if _turn == TURN_TABLE[turn]:
                            for _check in table[_hand][_turn]:
                                if _check == check_flag:
                                    for _action in table[_hand][_turn][_check]:
                                        match _action:
                                            case 'fold':
                                                shf += table[_hand][_turn][_check]['fold']
                                                so += table[_hand][_turn][_check]['fold']
                                                so_hi[1] += table[_hand][_turn][_check]['fold']
                                            case 'check':
                                                shch += table[_hand][_turn][_check]['check']
                                                so += table[_hand][_turn][_check]['check']
                                                so_hi[2] += table[_hand][_turn][_check]['check']
                                            case 'call':
                                                shc += table[_hand][_turn][_check]['call']
                                                so += table[_hand][_turn][_check]['call']
                                                so_hi[3] += table[_hand][_turn][_check]['call']
                                            case 'raise':
                                                shr += table[_hand][_turn][_check]['raise']
                                                so += table[_hand][_turn][_check]['raise']
                                                so_hi[4] += table[_hand][_turn][_check]['raise']
                                            case 'all in':
                                                sha += table[_hand][_turn][_check]['all in']
                                                so += table[_hand][_turn][_check]['all in']
                                                so_hi[5] += table[_hand][_turn][_check]['all in']
                                else:
                                    for _action in table[_hand][_turn][_check]:
                                        match _action:
                                            case 'fold':
                                                shf += table[_hand][_turn][_check]['fold']
                                            case 'check':
                                                shch += table[_hand][_turn][_check]['check']
                                            case 'call':
                                                shc += table[_hand][_turn][_check]['call']
                                            case 'raise':
                                                shr += table[_hand][_turn][_check]['raise']
                                            case 'all in':
                                                sha += table[_hand][_turn][_check]['all in']
                        else:
                            for _check in table[_hand][_turn]:
                                for _action in table[_hand][_turn][_check]:
                                    match _action:
                                        case 'fold':
                                            shf += table[_hand][_turn][_check]['fold']
                                        case 'check':
                                            shch += table[_hand][_turn][_check]['check']
                                        case 'call':
                                            shc += table[_hand][_turn][_check]['call']
                                        case 'raise':
                                            shr += table[_hand][_turn][_check]['raise']
                                        case 'all in':
                                            sha += table[_hand][_turn][_check]['all in']
                else:
                    for _turn in table[_hand]:
                        for _check in table[_hand][_turn]:
                            for _action in table[_hand][_turn][_check]:
                                match _action:
                                    case 'fold':
                                        shf += table[_hand][_turn][_check]['fold']
                                    case 'check':
                                        shch += table[_hand][_turn][_check]['check']
                                    case 'call':
                                        shc += table[_hand][_turn][_check]['call']
                                    case 'raise':
                                        shr += table[_hand][_turn][_check]['raise']
                                    case 'all in':
                                        sha += table[_hand][_turn][_check]['all in']

            if 0 in [sha, shr,shf,shc,shch] or count == 0:
                return 'error'
            tmp[player]['phi'][1] = shf/count
            tmp[player]['phi'][2] = shch/count
            tmp[player]['phi'][3] = shc/count
            tmp[player]['phi'][4] = shr/count
            tmp[player]['phi'][5] = sha/count
            tmp[player]['po'] = so/count
            tmp[player]['po_hi'][1] = so_hi[1]/shf
            tmp[player]['po_hi'][2] = so_hi[2]/shch
            tmp[player]['po_hi'][3] = so_hi[3]/shc
            tmp[player]['po_hi'][4] = so_hi[4]/shr
            tmp[player]['po_hi'][5] = so_hi[5]/sha

            for i in range(1,6):
                if tmp[player]['po'] != 0:
                    bruh = tmp[player]['phi'][i]*tmp[player]['po_hi'][i]/tmp[player]['po']
                    res[player][i] += bruh
                else:
                    return 'error'

        print(res[player])
    return res

def table_counting(counting_table):
    count = 0
    for hand in counting_table:
        for turn in counting_table[hand]:
            for check in counting_table[hand][turn]:
                for action in counting_table[hand][turn][check]:
                    count += counting_table[hand][turn][check][action]
    return count

def table_rescaling(data_table):
    counting_table = data_table.counting_table
    for hs in counting_table:
        for turn in counting_table[hs]:
            for check in counting_table[hs][turn]:
                for action in counting_table[hs][turn][check]:
                    counting_table[hs][turn][check][action] = counting_table[hs][turn][check][action]*RESCALING_SIZE/data_table.count
    data_table.count = table_counting(data_table.counting_table)
    return data_table
