from poker_ai.ai.ml.methods import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.constant import PLAYER
from poker_ai.poker.poker_component import Player, Hand, Deck

class Data_table():
    def __init__(self):
        self.counting_table = {i: {j: {k: {l:0 for l in ['fold', 'check', 'call', 'raise', 'all in']}
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for i in ['1', '2', '3', '4', '5']}
        self.data_observation = {'so': {a: {j: {k: 0
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for a in ['1', '2', '3', '4', '5']},\
                        'so_hi': {i: {j: {k: {l:0 for l in ['fold', 'check', 'call', 'raise', 'all in']}
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}
                        for i in ['1', '2', '3', '4', '5']}}
        self.data_action = {'fold':0, 'check':0, 'call':0, 'raise':0, 'all in':0} # shf, shch, shc, shr and sha respectively in modelling
        self.count = 0
    def refresh_table(self):
        self.__init__()

def table_building(history, tables, hs, check_flag):
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    data = history[-1]
    counting_table = tables.counting_table
    match data[1]:
        case 0:
            counting_table[hs]['preflop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 3:
            counting_table[hs]['flop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 4:
            counting_table[hs]['turn'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 5:
            counting_table[hs]['river'][check_flag][ACTION_TABLE[data[2]]] += 1
    tables.count += 1
    return tables

def recording(tables, history, checkout, player_hand, board):
    if history == []:
        return '????'
    # TODO Add hs in range(1, 5)
    hs = '?'

    if 2 in checkout and 3 not in checkout:
        check_flag = 'can only check'
    elif 2 not in checkout and 3 in checkout:
        check_flag = "can only call"
    elif 2 not in checkout and 3 not in checkout:
        check_flag = "can't check or call"
    else:
        raise Exception('wait wot???')
    tables = table_building(history, tables, hs, check_flag)
    return tables

def magical_four(tables, turn, checkout):
    # the constants here are just to translate from a format to another
    ACTION = {1: 'fold', 2:'check', 3:'call', 4:'raise', 5:'all in'}
    TURN_TABLE = ['preflop','flop','turn','river']
    tmp = {i:{'phi':[None,0,0,0,0,0],\
            'po':0,\
            'po_hi':[0,0,0,0,0,0],\
            } for i in tables}
    bruh={}
    
    for player in tables:
        table = tables[player]
        count = table.count
        counting_table = table.counting_table
        _turn = TURN_TABLE[turn]
        data_observation = table.data_observation
        data_action = table.data_action
        res = {i: 0 for i in ['fold','check','call','raise','all in']}
        if 2 in checkout and 3 not in checkout:
            check_flag = 'can only check'
        elif 2 not in checkout and 3 in checkout:
            check_flag = "can only call"
        elif 2 not in checkout and 3 not in checkout:
            check_flag = "can't check or call"
        else:
            raise Exception('wait wot???')
        for hs in counting_table:
            tmp[player]['phi'][1] = data_action['fold']/count
            tmp[player]['phi'][2] = data_action['check']/count
            tmp[player]['phi'][3] = data_action['call']/count
            tmp[player]['phi'][4] = data_action['raise']/count
            tmp[player]['phi'][5] = data_action['all in']/count
            tmp[player]['po'] = data_observation['so'][hs][_turn][check_flag]/count
            tmp[player]['po_hi'][1] = data_observation['so_hi'][hs][_turn][check_flag]['fold']/data_action['fold']
            tmp[player]['po_hi'][2] = data_observation['so_hi'][hs][_turn][check_flag]['check']/data_action['check']
            tmp[player]['po_hi'][3] = data_observation['so_hi'][hs][_turn][check_flag]['call']/data_action['call']
            tmp[player]['po_hi'][4] = data_observation['so_hi'][hs][_turn][check_flag]['raise']/data_action['raise']
            tmp[player]['po_hi'][5] = data_observation['so_hi'][hs][_turn][check_flag]['all in']/data_action['all in']
            for i in range(1,6):
                bruh = tmp[player]['phi'][i]*tmp[player]['po_hi'][i]/tmp[player]['po']
                res[ACTION[i]] += bruh
        bruh[player]=res.copy()
    return bruh


def table_counting(counting_table):
    count = 0
    for hs in counting_table:
        for turn in counting_table[hs]:
            for check in counting_table[hs][turn]:
                for action in counting_table[hs][turn][check]:
                    count += counting_table[hs][turn][check][action]
    return count

def preprocess_table(tables):
    table = tables.counting_table
    data_observation = tables.data_observation
    data_action = tables.data_action
    for _hs in table:
        for _turn in table[_hs]:
            for _check in table[_hs][_turn]:
                for _action in table[_hs][_turn][_check]:
                    match _action:
                        case 'fold':
                            data_action['fold'] += table[_hs][_turn][_check]['fold']
                            data_observation['so'][_hs][_turn][_check] += table[_hs][_turn][_check]['fold']
                            data_observation['so_hi'][_hs][_turn][_check][_action] += table[_hs][_turn][_check]['fold']
                        case 'check':
                            data_action['check'] += table[_hs][_turn][_check]['check']
                            data_observation['so'][_hs][_turn][_check] += table[_hs][_turn][_check]['check']
                            data_observation['so_hi'][_hs][_turn][_check][_action] += table[_hs][_turn][_check]['check']
                        case 'call':
                            data_action['call'] += table[_hs][_turn][_check]['call']
                            data_observation['so'][_hs][_turn][_check] += table[_hs][_turn][_check]['call']
                            data_observation['so_hi'][_hs][_turn][_check][_action] += table[_hs][_turn][_check]['call']
                        case 'raise':
                            data_action['raise'] += table[_hs][_turn][_check]['raise']
                            data_observation['so'][_hs][_turn][_check] += table[_hs][_turn][_check]['raise']
                            data_observation['so_hi'][_hs][_turn][_check][_action] += table[_hs][_turn][_check]['raise']
                        case 'all in':
                            data_action['all in'] += table[_hs][_turn][_check]['all in']
                            data_observation['so'][_hs][_turn][_check] += table[_hs][_turn][_check]['all in']
                            data_observation['so_hi'][_hs][_turn][_check][_action] += table[_hs][_turn][_check]['all in']
    return (data_observation, data_action)

def table_record(tables, history, checkout, players):
    # record the game at the end of every game
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    TURN_TABLE = ['preflop','flop','turn','river']

    # TODO add hs eval
    hs = '?'

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
        counting_table[hs][turn][check_flag][action] += 1

        # update data_action
        data_action = tables[player].data_action
        data_action[action] += 1

        # update data_observation
        data_observation = tables[player].data_observation
        data_observation['so'][hs][turn][check_flag] += 1
        data_observation['so_hi'][hs][turn][check_flag][action] += 1

        # update count
        tables[player].count += 1

def enumurate(player_hand, board, num_players):
    player = Player(player_hand, 'test', 100)
    hands = Deck().cards
    card = []
    d = []
    for i in range(len(hands)):
        for j in range(len(hands)):
            card.append([hands[i],hands[j]])
    for hand in card:
        player.hand.cards = hand
        win = multi_process_eval_func_but_in_opponent_modelling(player, num_players, board)[0]
        d.append((win,hand))
    d.sort()
    for win, hand in d:
        pass

