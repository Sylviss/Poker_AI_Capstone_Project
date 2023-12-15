class Rate_recorder():
    def __init__(self):
        self.win = 0
    def refresh(self):
        self.__init__()

class Data_table():
    def __init__(self):
        self.counting_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'medium', 'weak']}
        self.data_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'medium', 'weak']}
        self.count = 0
    def refresh_table(self):
        self.__init__()

def table_building(history, tables, hs):
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    data = history[-1]
    counting_table = tables[data[0]]
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

def opponent_modelling(history, tables, recorder, turn):
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

    TURN_TABLE = ['preflop',None,None,'flop','turn','river']

    if recorder >= 60:
        hs = 'strong'
    elif 40 <= recorder < 60:
        hs = 'medium'
    else:
        hs = 'weak'
    tables = table_building(history, tables, hs)
    shs = [0, 0, 0, 0, 0, 0]
    sturn = [0, 0, 0, 0, 0, 0]
    shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
    for player in tables:
        table = tables[player]
        for _hs in table:
            if _hs == hs:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += 1
                                    shs[0] += 1
                                    sturn[0] += 1
                                    shs[1] += 1
                                    sturn[1] += 1
                                case 'check':
                                    shch += 1
                                    shs[0] += 1
                                    sturn[0] += 1
                                    shs[2] += 1
                                    sturn[2] += 1
                                case 'call':
                                    shc += 1
                                    shs[0] += 1
                                    sturn[0] += 1
                                    shs[3] += 1
                                    sturn[3] += 1
                                case 'raise':
                                    shr += 1
                                    shs[0] += 1
                                    sturn[0] += 1
                                    shs[4] += 1
                                    sturn[4] += 1
                                case 'all in':
                                    sha += 1
                                    shs[0] += 1
                                    sturn[0] += 1
                                    shs[5] += 1
                                    sturn[5] += 1
                    else:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += 1
                                    shs[0] += 1
                                    shs[1] += 1
                                case 'check':
                                    shch += 1
                                    shs[0] += 1
                                    shs[2] += 1
                                case 'call':
                                    shc += 1
                                    shs[0] += 1
                                    shs[3] += 1
                                case 'raise':
                                    shr += 1
                                    shs[0] += 1
                                    shs[4] += 1
                                case 'all in':
                                    sha += 1
                                    shs[0] += 1
                                    shs[5] += 1
            else:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += 1
                                    sturn[0] += 1
                                    sturn[1] += 1
                                case 'check':
                                    shch += 1
                                    sturn[0] += 1
                                    sturn[2] += 1
                                case 'call':
                                    shc += 1
                                    sturn[0] += 1
                                    sturn[3] += 1
                                case 'raise':
                                    shr += 1
                                    sturn[0] += 1
                                    sturn[4] += 1
                                case 'all in':
                                    sha += 1
                                    sturn[0] += 1
                                    sturn[5] += 1
                    else:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += 1
                                case 'check':
                                    shch += 1
                                case 'call':
                                    shc += 1
                                case 'raise':
                                    shr += 1
                                case 'all in':
                                    sha += 1
    
