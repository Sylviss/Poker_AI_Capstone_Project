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
        self.data_action = {'fold':0, 'check':0, 'call':0, 'raise':0, 'all in':0} # shf, shch, shc, shr and sha respectively in modelling
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

def magical_four(tables, turn, checkout):
    # the constants here are just to translate from a format to another
    ACTION = {1: 'fold', 2:'check', 3:'call', 4:'raise', 5:'all in'}
    TURN_TABLE = ['preflop','flop','turn','river']
    tmp = {i:{'phi':[None,0,0,0,0,0],\
            'po':0,\
            'po_hi':[0,0,0,0,0,0],\
            } for i in tables}
    for player in tables:
        table = tables[player]
        count = table.count
        counting_table = table.counting_table
        _turn = TURN_TABLE[turn]
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
        for hand in counting_table:
            tmp[player]['phi'][1] = data_action['fold']/count
            tmp[player]['phi'][2] = data_action['check']/count
            tmp[player]['phi'][3] = data_action['call']/count
            tmp[player]['phi'][4] = data_action['raise']/count
            tmp[player]['phi'][5] = data_action['all in']/count
            tmp[player]['po'] = data_observation['so'][hand][_turn][check_flag]/count
            tmp[player]['po_hi'][1] = data_observation['so_hi'][hand][_turn][check_flag]['fold']/data_action['fold']
            tmp[player]['po_hi'][2] = data_observation['so_hi'][hand][_turn][check_flag]['check']/data_action['check']
            tmp[player]['po_hi'][3] = data_observation['so_hi'][hand][_turn][check_flag]['call']/data_action['call']
            tmp[player]['po_hi'][4] = data_observation['so_hi'][hand][_turn][check_flag]['raise']/data_action['raise']
            tmp[player]['po_hi'][5] = data_observation['so_hi'][hand][_turn][check_flag]['all in']/data_action['all in']
            for i in range(1,6):
                bruh = tmp[player]['phi'][i]*tmp[player]['po_hi'][i]/tmp[player]['po']
                res[ACTION[i]] += bruh/1326
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
                            data_action['fold'] += table[_hand][_turn][_check]['fold']
                            data_observation['so'][_hand][_turn][_check] += table[_hand][_turn][_check]['fold']
                            data_observation['so_hi'][_hand][_turn][_check][_action] += table[_hand][_turn][_check]['fold']
                        case 'check':
                            data_action['check'] += table[_hand][_turn][_check]['check']
                            data_observation['so'][_hand][_turn][_check] += table[_hand][_turn][_check]['check']
                            data_observation['so_hi'][_hand][_turn][_check][_action] += table[_hand][_turn][_check]['check']
                        case 'call':
                            data_action['call'] += table[_hand][_turn][_check]['call']
                            data_observation['so'][_hand][_turn][_check] += table[_hand][_turn][_check]['call']
                            data_observation['so_hi'][_hand][_turn][_check][_action] += table[_hand][_turn][_check]['call']
                        case 'raise':
                            data_action['raise'] += table[_hand][_turn][_check]['raise']
                            data_observation['so'][_hand][_turn][_check] += table[_hand][_turn][_check]['raise']
                            data_observation['so_hi'][_hand][_turn][_check][_action] += table[_hand][_turn][_check]['raise']
                        case 'all in':
                            data_action['all in'] += table[_hand][_turn][_check]['all in']
                            data_observation['so'][_hand][_turn][_check] += table[_hand][_turn][_check]['all in']
                            data_observation['so_hi'][_hand][_turn][_check][_action] += table[_hand][_turn][_check]['all in']
    return (data_observation, data_action)

def table_record(tables, history, checkout, players):
    # record the game at the end of every game
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    TURN_TABLE = ['preflop','flop','turn','river']
    RANK = [None,'2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUIT = ['c','d','h','s']
    hands = {}
    for player in players:
        tmp = []
        hand = player.hand.cards
        for card in hand:
            tmp.append(RANK[card.rank]+SUIT[card.suit])
        hands[player.name] = ' '.join(list(sorted(tmp)))
        print(hands)
    for i in range(len(history)):
        action = ACTION_TABLE[history[i][2]]
        _checkout = checkout[i]
        turn = TURN_TABLE[history[i][1]]
        player =  history[i][0]
        if 2 in _checkout and 3 not in _checkout:
            check_flag = 'can only check'
        elif 2 not in _checkout and 3 in _checkout:
            check_flag = "can only call"
        elif 2 not in _checkout and 3 not in _checkout:
            check_flag = "can't check or call"
        else:
            raise Exception('wait wot???')
        
        # update counting_table
        counting_table = tables[player].counting_table
        counting_table[hands[player]][turn][check_flag][action] += 1

        # update data_action
        data_action = tables[player].data_action
        data_action[action] += 1

        # update data_observation
        data_observation = tables[player].data_observation
        data_observation['so'][hands[player]][turn][check_flag] += 1
        data_observation['so_hi'][hands[player]][turn][check_flag][action] += 1

        # update count
        tables[player].count += 1
