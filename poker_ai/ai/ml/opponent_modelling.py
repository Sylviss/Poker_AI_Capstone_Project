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

    if 0.45<= recorder.win:
        hs = 'strong'
    elif 0.35 <= recorder.win < 0.45:
        hs = 'medium'
    else:
        hs = 'weak'
    tables = table_building(history, tables, hs)
    tmp = {i:{'phi':[None,0,0,0,0,0],\
              'phs':[0,0,0,0,0,0],\
              'pturn':[0,0,0,0,0,0],\
             } for i in tables}
    res = {i:[] for i in tables}
    for player in tables:
        table = tables[player].counting_table
        count = tables[player].count
        shs = [0, 0, 0, 0, 0, 0]
        sturn = [0, 0, 0, 0, 0, 0]
        shf, shch, shc, shr, sha = 0, 0, 0, 0, 0
        for _hs in table:
            if _hs == hs:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                    shs[0] += table[_hs][_turn]['fold']
                                    sturn[0] += table[_hs][_turn]['fold']
                                    shs[1] += table[_hs][_turn]['fold']
                                    sturn[1] += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                    shs[0] += table[_hs][_turn]['check']
                                    sturn[0] += table[_hs][_turn]['check']
                                    shs[2] += table[_hs][_turn]['check']
                                    sturn[2] += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                    shs[0] += table[_hs][_turn]['call']
                                    sturn[0] += table[_hs][_turn]['call']
                                    shs[3] += table[_hs][_turn]['call']
                                    sturn[3] += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                    shs[0] += table[_hs][_turn]['raise']
                                    sturn[0] += table[_hs][_turn]['raise']
                                    shs[4] += table[_hs][_turn]['raise']
                                    sturn[4] += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
                                    shs[0] += table[_hs][_turn]['all in']
                                    sturn[0] += table[_hs][_turn]['all in']
                                    shs[5] += table[_hs][_turn]['all in']
                                    sturn[5] += table[_hs][_turn]['all in']
                    else:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                    shs[0] += table[_hs][_turn]['fold']
                                    shs[1] += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                    shs[0] += table[_hs][_turn]['check']
                                    shs[2] += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                    shs[0] += table[_hs][_turn]['call']
                                    shs[3] += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                    shs[0] += table[_hs][_turn]['raise']
                                    shs[4] += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
                                    shs[0] += table[_hs][_turn]['all in']
                                    shs[5] += table[_hs][_turn]['all in']
            else:
                for _turn in table[_hs]:
                    if _turn == TURN_TABLE[turn]:
                        for _action in table[_hs][_turn]:
                            match _action:
                                case 'fold':
                                    shf += table[_hs][_turn]['fold']
                                    sturn[0] += table[_hs][_turn]['fold']
                                    sturn[1] += table[_hs][_turn]['fold']
                                case 'check':
                                    shch += table[_hs][_turn]['check']
                                    sturn[0] += table[_hs][_turn]['check']
                                    sturn[2] += table[_hs][_turn]['check']
                                case 'call':
                                    shc += table[_hs][_turn]['call']
                                    sturn[0] += table[_hs][_turn]['call']
                                    sturn[3] += table[_hs][_turn]['call']
                                case 'raise':
                                    shr += table[_hs][_turn]['raise']
                                    sturn[0] += table[_hs][_turn]['raise']
                                    sturn[4] += table[_hs][_turn]['raise']
                                case 'all in':
                                    sha += table[_hs][_turn]['all in']
                                    sturn[0] += table[_hs][_turn]['all in']
                                    sturn[5] += table[_hs][_turn]['all in']
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
        tmp[player]['phs'][0] = shs[0]/count
        tmp[player]['phs'][1] = shs[1]/count
        tmp[player]['phs'][2] = shs[2]/count
        tmp[player]['phs'][3] = shs[3]/count
        tmp[player]['phs'][4] = shs[4]/count
        tmp[player]['phs'][5] = shs[5]/count
        tmp[player]['pturn'][0] = sturn[0]/count
        tmp[player]['pturn'][1] = sturn[1]/count
        tmp[player]['pturn'][2] = sturn[2]/count
        tmp[player]['pturn'][3] = sturn[3]/count
        tmp[player]['pturn'][4] = sturn[4]/count
        tmp[player]['pturn'][5] = sturn[5]/count

    for player in tables:
        print(tmp[player])
        for i in range(1,6):
            bruh = ((tmp[player]['phi'][i])*(tmp[player]['phs'][i])*(tmp[player]['pturn'][i]))/((tmp[player]['phs'][0])*(tmp[player]['pturn'][0]))
            res[player].append(bruh)
    return res
