from poker_ai.ai.ml.methods import multi_process_eval_func_but_in_opponent_modelling

class Rate_recorder():
    def __init__(self):
        self.win = 0.0
    def refresh(self):
        self.__init__()

class Data_table():
    def __init__(self):
        self.counting_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'flop', 'turn', 'river']}\
                        for i in ['strong', 'medium', 'weak']}
        self.data_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'flop', 'turn', 'showdown']}\
                        for i in ['strong', 'medium', 'weak']}
        self.count = 45
    def refresh_table(self):
        self.__init__()

def table_building(history, tables, hs):
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    data = history[-1]
    counting_table = tables[data[0]].counting_table
    match data[1]:
        case 0:
            counting_table[hs]['preflop'][ACTION_TABLE[data[2]]] += 1
        case 3:
            counting_table[hs]['flop'][ACTION_TABLE[data[2]]] += 1
        case 4:
            counting_table[hs]['turn'][ACTION_TABLE[data[2]]] += 1
        case 5:
            counting_table[hs]['river'][ACTION_TABLE[data[2]]] += 1
    tables[data[0]].count += 1
    return tables

def opponent_modelling(history, tables, turn, human, board, num_player):
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

    recorder = multi_process_eval_func_but_in_opponent_modelling(human, num_player, board)[0]
    print(recorder)

    if 0.45<= recorder:
        hs = 'weak'
    elif 0.35 <= recorder < 0.45:
        hs = 'medium'
    else:
        hs = 'strong'
    tables = table_building(history, tables, hs)
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
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                    so += table[_hs][_turn]['fold']
                                    so_hi[1] += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                    so += table[_hs][_turn]['check']
                                    so_hi[2] += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                    so += table[_hs][_turn]['call']
                                    so_hi[3] += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                    so += table[_hs][_turn]['raise']
                                    so_hi[4] += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
                                    so += table[_hs][_turn]['all in']
                                    so_hi[5] += table[_hs][_turn]['all in']
                    else:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
            else:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
                    else:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
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
    print(res)
    return (res, tables)

def table_counting(counting_table):
    count = 0
    for hs in counting_table:
        for turn in counting_table[hs]:
            for action in counting_table[hs][turn]:
                count += counting_table[hs][turn][action]
    return count
