from poker_ai.constant import RESCALING_SIZE
from poker_ai.poker.poker_component import card_to_str

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
        self.data_observation = {'so': {a: {j: {k: 0
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for a in hands},\
                        'so_hi': {i: {j: {k: {l:0 for l in ['fold', 'check', 'call', 'raise', 'all in']}
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for i in hands}}
        self.data_action = {'fold':0, 'call':0, 'check':0, 'raise':0, 'all_in':0}
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

def modelling(tables, turn, checkout):
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
    res = {i:[0 for _ in range(7)] for i in tables}

    for player in tables:
        table = tables[player].counting_table
        count = table_counting(tables[player].counting_table)
        so = 0
        so_hi = [0, 0, 0, 0, 0, 0]
        shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
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

def magiccal_four(tables, turn, checkout):
    ACTION = {1: 'fold', 2:'check', 3:'call', 4:'raise', 5:'all in'}
    TURN_TABLE = ['preflop','flop','turn','river']
    tmp = {i:{'phi':[None,0,0,0,0,0],\
            'po':0,\
            'po_hi':[0,0,0,0,0,0],\
            } for i in tables}
    for player in tables:
        table = tables[player]
        count = table.count
        turn = TURN_TABLE[turn]
        data_observation = table.data_observation
        data_action = table.data_action
        action = 2
        res = {i: 0 for i in ['fold','check','call','raise','all in']}
        if 2 in checkout and 3 not in checkout:
            check_flag = 'can only check'
        elif 2 not in checkout and 3 in checkout:
            check_flag = "can only call"
        elif 2 not in checkout and 3 not in checkout:
            check_flag = "can't check or call"
        else:
            raise Exception('wait wot???')
        for hand in table:
            tmp[player]['phi'][1] = data_action['fold']/count
            tmp[player]['phi'][2] = data_action['check']/count
            tmp[player]['phi'][3] = data_action['call']/count
            tmp[player]['phi'][4] = data_action['raise']/count
            tmp[player]['phi'][5] = data_action['all in']/count
            tmp[player]['po'] = data_observation['so'][hand][turn][check_flag]/count
            tmp[player]['po_hi'][1] = data_observation[hand][turn][check_flag]['fold']/data_action['fold']
            tmp[player]['po_hi'][2] = data_observation[hand][turn][check_flag]['check']/data_action['check']
            tmp[player]['po_hi'][3] = data_observation[hand][turn][check_flag]['call']/data_action['call']
            tmp[player]['po_hi'][4] = data_observation[hand][turn][check_flag]['raise']/data_action['raise']
            tmp[player]['po_hi'][5] = data_observation[hand][turn][check_flag]['all in']/data_action['all in']
            for i in range(1,6):
                bruh = tmp[player]['phi'][i]*tmp[player]['po_hi'][i]/tmp[player]['po']
                res[ACTION[i]] += bruh
        print(res)

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
    for hand in counting_table:
        for turn in counting_table[hand]:
            for check in counting_table[hand][turn]:
                for action in counting_table[hand][turn][check]:
                    counting_table[hand][turn][check][action] = counting_table[hand][turn][check][action]*RESCALING_SIZE/data_table.count
    data_table.count = table_counting(data_table.counting_table)
    return data_table

def preprocess_table(tables):
    table = tables.counting_table
    data_observation = tables.data_observation
    data_action = tables.data_action
    for _hand in table:
        for _turn in table[_hand]:
            for _check in table[_hand][_turn]:
                for _action in table[_hand][_turn][_check]:
                    match _action:
                        case 'fold':
                            data_action['s_actions']['fold'] += 1
                            data_observation['so'][_hand][_turn][_check] += 1
                            data_observation['so_hi'][_hand][_turn][_check][_action] += 1
                        case 'check':
                            data_action['s_actions']['check'] += 1
                            data_observation['so'][_hand][_turn][_check] += 1
                            data_observation['so_hi'][_hand][_turn][_check][_action] += 1
                        case 'call':
                            data_action['s_actions']['call'] += 1
                            data_observation['so'][_hand][_turn][_check] += 1
                            data_observation['so_hi'][_hand][_turn][_check][_action] += 1
                        case 'raise':
                            data_action['s_actions']['raise'] += 1
                            data_observation['so'][_hand][_turn][_check] += 1
                            data_observation['so_hi'][_hand][_turn][_check][_action] += 1
                        case 'all in':
                            data_action['s_actions']['all in'] += 1
                            data_observation['so'][_hand][_turn][_check] += 1
                            data_observation['so_hi'][_hand][_turn][_check][_action] += 1
    return (data_observation, data_action)

def table_record(tables, history, turn, checkout):
    pass
