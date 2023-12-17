from poker_ai.ai.ml.methods import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.constant import RESCALING_SIZE

class Rate_recorder():
    def __init__(self):
        self.win = 0.0
    def refresh(self):
        self.__init__()

class Data_table():
    def __init__(self):
        self.counting_table = {i: {j: {k: {l:10**-9 for l in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for k in ['can only check', 'can only call', "can't check or call"]}
                        for j in ['preflop', 'flop', 'turn', 'river']}\
                        for i in ['strong', 'medium', 'weak']}
        self.data_table = {i: {j: {k: {l:0.0000001 for l in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for k in ['can check', "can't check"]}
                        for j in ['preflop', 'flop', 'turn', 'showdown']}\
                        for i in ['strong', 'medium', 'weak']}
        self.count = 3*4*2*5
    def refresh_table(self):
        self.__init__()

def table_building(history, tables, hs, check_flag):
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    data = history[-1]
    counting_table = tables[data[0]].counting_table
    match data[1]:
        case 0:
            counting_table[hs]['preflop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 3:
            counting_table[hs]['flop'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 4:
            counting_table[hs]['turn'][check_flag][ACTION_TABLE[data[2]]] += 1
        case 5:
            counting_table[hs]['river'][check_flag][ACTION_TABLE[data[2]]] += 1
    tables[data[0]].count += 1
    return tables

def opponent_modelling(history, tables, turn, human, board, num_player, checkout):
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
    if history == []:
        return '????'

    TURN_TABLE = ['preflop','flop','turn','river']

    recorder = multi_process_eval_func_but_in_opponent_modelling(human, num_player, board)[0]
    print(recorder)

    if 0.45<= recorder:
        hs = 'weak'
    elif 0.35 <= recorder < 0.45:
        hs = 'medium'
    else:
        hs = 'strong'
    if 2 in checkout and 3 not in checkout:
        check_flag = 'can only check'
    elif 2 not in checkout and 3 in checkout:
        check_flag = "can only call"
    elif 2 not in checkout and 3 not in checkout:
        check_flag = "can't check or call"
    else:
        raise Exception('wait wot???')
    tables = table_building(history, tables, hs, check_flag)
    tmp = {i:{'phi':[None,0,0,0,0,0],\
              'po':0,\
              'po_hi':[0,0,0,0,0,0],\
             } for i in tables}
    res = {i:[] for i in tables}

    for player in tables:
        table = tables[player].counting_table
        count = tables[player].count
        so = 0
        so_hi = [0, 0, 0, 0, 0, 0]
        shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
        for _hs in table:
            if _hs == hs:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _check in table[_hs][_turn]:
                            match _check:
                                case 'can only check':
                                    if _check == check_flag:
                                        for _action in table[_hs][_turn][_check]:
                                            match _action:
                                                case 'fold':
                                                    shf += table[_hs][_turn][_check]['fold']
                                                    so += table[_hs][_turn][_check]['fold']
                                                    so_hi[1] += table[_hs][_turn][_check]['fold']
                                                case 'check':
                                                    shch += table[_hs][_turn][_check]['check']
                                                    so += table[_hs][_turn][_check]['check']
                                                    so_hi[2] += table[_hs][_turn][_check]['check']
                                                case 'raise':
                                                    shr += table[_hs][_turn][_check]['raise']
                                                    so += table[_hs][_turn][_check]['raise']
                                                    so_hi[4] += table[_hs][_turn][_check]['raise']
                                                case 'all in':
                                                    sha += table[_hs][_turn][_check]['all in']
                                                    so += table[_hs][_turn][_check]['all in']
                                                    so_hi[5] += table[_hs][_turn][_check]['all in']
                                    else:
                                        for _action in table[_hs][_turn][_check]:
                                            match _action:
                                                case 'fold':
                                                    shf += table[_hs][_turn][_check]['fold']
                                                case 'check':
                                                    shch += table[_hs][_turn][_check]['check']
                                                case 'raise':
                                                    shr += table[_hs][_turn][_check]['raise']
                                                case 'all in':
                                                    sha += table[_hs][_turn][_check]['all in']
                                case 'can only call':
                                    if _check == check_flag:
                                        for _action in table[_hs][_turn][_check]:
                                            match _action:
                                                case 'fold':
                                                    shf += table[_hs][_turn][_check]['fold']
                                                    so += table[_hs][_turn][_check]['fold']
                                                    so_hi[1] += table[_hs][_turn][_check]['fold']
                                                case 'call':
                                                    shc += table[_hs][_turn][_check]['call']
                                                    so += table[_hs][_turn][_check]['call']
                                                    so_hi[3] += table[_hs][_turn][_check]['call']
                                                case 'raise':
                                                    shr += table[_hs][_turn][_check]['raise']
                                                    so += table[_hs][_turn][_check]['raise']
                                                    so_hi[4] += table[_hs][_turn][_check]['raise']
                                                case 'all in':
                                                    sha += table[_hs][_turn][_check]['all in']
                                                    so += table[_hs][_turn][_check]['all in']
                                                    so_hi[5] += table[_hs][_turn][_check]['all in']
                                    else:
                                        for _action in table[_hs][_turn][_check]:
                                            match _action:
                                                case 'fold':
                                                    shf += table[_hs][_turn][_check]['fold']
                                                case 'call':
                                                    shc += table[_hs][_turn][_check]['call']
                                                case 'raise':
                                                    shr += table[_hs][_turn][_check]['raise']
                                                case 'all in':
                                                    sha += table[_hs][_turn][_check]['all in']
                                case "can't check or call":
                                    for _action in table[_hs][_turn][_check]:
                                        match _action:
                                            case 'fold':
                                                shf += table[_hs][_turn][_check]['fold']
                                                so += table[_hs][_turn][_check]['fold']
                                                so_hi[1] += table[_hs][_turn][_check]['fold']
                                            case 'raise':
                                                shr += table[_hs][_turn][_check]['raise']
                                                so += table[_hs][_turn][_check]['raise']
                                                so_hi[4] += table[_hs][_turn][_check]['raise']
                                            case 'all in':
                                                sha += table[_hs][_turn][_check]['all in']
                                                so += table[_hs][_turn][_check]['all in']
                                                so_hi[5] += table[_hs][_turn][_check]['all in']
                    else:
                        for _check in table[_hs][_turn]:
                            for _action in table[_hs][_turn][_check]:
                                match _action:
                                    case 'fold':
                                        shf += table[_hs][_turn][_check]['fold']
                                        so += table[_hs][_turn][_check]['fold']
                                        so_hi[1] += table[_hs][_turn][_check]['fold']
                                    case 'check':
                                        shch += table[_hs][_turn][_check]['check']
                                        so += table[_hs][_turn][_check]['check']
                                        so_hi[2] += table[_hs][_turn][_check]['check']
                                    case 'call':
                                        shc += table[_hs][_turn][_check]['call']
                                        so += table[_hs][_turn][_check]['call']
                                        so_hi[3] += table[_hs][_turn][_check]['call']
                                    case 'raise':
                                        shr += table[_hs][_turn][_check]['raise']
                                        so += table[_hs][_turn][_check]['raise']
                                        so_hi[4] += table[_hs][_turn][_check]['raise']
                                    case 'all in':
                                        sha += table[_hs][_turn][_check]['all in']
                                        so += table[_hs][_turn][_check]['all in']
                                        so_hi[5] += table[_hs][_turn][_check]['all in']
            else:
                for _turn in table[_hs]:
                    for _check in table[_hs][_turn]:
                        for _action in table[_hs][_turn][_check]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn][_check]['fold']
                                case 'check':
                                    shch += table[_hs][_turn][_check]['check']
                                case 'call':
                                    shc += table[_hs][_turn][_check]['call']
                                case 'raise':
                                    shr += table[_hs][_turn][_check]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn][_check]['all in']

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

    for player in tables:
        for i in range(1,6):
            bruh = tmp[player]['phi'][i]*tmp[player]['po_hi'][i]/tmp[player]['po']
            res[player].append(bruh)
    return (res, tables)

def table_counting(counting_table):
    count = 0
    for hs in counting_table:
        for turn in counting_table[hs]:
            for check in counting_table[hs][turn]:
                for action in counting_table[hs][turn][check]:
                    count += counting_table[hs][turn][check][action]
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
