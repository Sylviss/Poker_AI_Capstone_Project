SLANSKY_GROUP = {
    "AA": 1, "AKs": 1, "KK": 1, "QQ": 1, "JJ": 1,
    "AK": 2, "AQs": 2, "AJs": 2, "KQs": 2, "TT": 2,
    "AQ": 3, "ATs": 3, "KJs": 3, "QJs": 3, "JTs": 3, "99": 3,
    "AJ": 4, "KQ": 4, "KTs": 4, "QTs": 4, "J9s": 4, "T9s": 4, "98s": 4, "88": 4,
    "A9s": 5, "A8s": 5, "A7s": 5, "A6s": 5, "A5s": 5, "A4s": 5, "A3s": 5, "A2s": 5, "KJ": 5, "QJ": 5, "JT": 5, "Q9s": 5, "T8s": 5, "97s": 5, "87s": 5, "77": 5, "76s": 5, "66": 5,
    "AT": 6, "KT": 6, "QT": 6, "J8s": 6, "86s": 6, "75s": 6, "65s": 6, "55": 6, "54s": 6,
    "K9s": 7, "K8s": 7, "K7s": 7, "K6s": 7, "K5s": 7, "K4s": 7, "K3s": 7, "K2s": 7, "J9": 7, "T9": 7, "98": 7, "64s": 7, "53s": 7, "44": 7, "43s": 7, "33": 7, "22": 7,
    "A9": 8, "K9": 8, "Q9": 8, "J8": 8, "J7s": 8, "T8": 8, "96s": 8, "87": 8, "85s": 8, "76": 8, "74s": 8, "65": 8, "54": 8, "42s": 8, "32s": 8,
}

class Data_table():
    def __init__(self):
        self.counting_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'weak', 'unknown']}
        self.data_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'weak', 'unknown']}
        self.count = 0
    def refresh_table(self):
        self.counting_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'weak', 'unknown']}
        self.count = 0
        self.data_table = {i: {j: {k: 0 for k in ['fold', 'check', 'call', 'raise', 'all in']}\
                        for j in ['preflop', 'mid_game', 'showdown']}\
                        for i in ['strong', 'weak', 'unknown']}


def opponent_modelling(history, players, tables, hand_strength = 'strong'):
    '''
    a function to model the type of opponent
    Input:
    Output:
    a tuple ({type of oppent},{list of move prob}) where:
        -) type of opponent is an int:
            +) 0: Conservative-tight
            +) 1: Conservative-loose
            +) 2: Agressive-tight
            +) 3: Agressive-loose
        -) list of move prob is a list that list all move prob
    '''
    flags = {i.name:False if i.state == 4 else True for i in players}
    ACTION_TABLE = [None, 'check', 'call', 'call', 'raise', 'raise', 'raise', 'fold', 'all in']
    for data in history[::-1]:
        id = data[0].split()[-1]
        if flags[data[0]]:
            hand = players[int(id)-1].hand.starting_hand_str()
            if hand not in SLANSKY_GROUP:
                hs = 'weak'
            else:
                if SLANSKY_GROUP[hand] <= 6:
                    hs = 'strong'
                else:
                    hs = 'weak'
        else:
            hs = 'unknown'
        counting_table = tables[data[0]].counting_table
        match data[1]:
            case 0:
                counting_table[hs]['preflop'][ACTION_TABLE[data[2]]] += 1
            case 3 | 4:
                counting_table[hs]['mid_game'][ACTION_TABLE[data[2]]] += 1
            case 5:
                counting_table[hs]['showdown'][ACTION_TABLE[data[2]]] += 1
        tables[data[0]].count += 1
    for table in tables:
        print(table,'\n',tables[table].counting_table,'\n')
