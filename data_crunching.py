import json
from poker_ai.datasets.data_extract import main
from poker_ai.poker.poker_component import Card, Hand, Player
from poker_ai.ai.eval_func import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.ai.ml.opponent_modelling import Data_table, Rate_recorder, table_building

def data_crunch():
    RANK = {'2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, 'T':9, 'J':10, 'Q':11, 'K':12, 'A':13}
    SUIT = {'d':1, 'h':2, 's':3, 'c':0}
    ACTIONS = {1:8, 2:1, 3:2, 4:4, 5:7}
    dataset = main()
    hands = {}
    actions = {}
    table = {'default':Data_table()}
    test = Player(Hand(), 'bruh', 4000)
    for datapack in dataset:
        for player_dict in datapack['players']:
            hands[player_dict['player_name']]=player_dict['player_hand']
            actions[player_dict['player_name']] = {i:[] for i in [0,3,4,5]}
        for i in [0,3,4,5]:
            bruh = datapack['actions'][i]
            if bruh != None:
                for bruhbruh in bruh:
                    actions[bruhbruh[0]][i].append(ACTIONS[bruhbruh[1][0]])
        for player in hands:
            hand_tmp = hands[player]
            hand = []
            for card in hand_tmp:
                a, b = card[0], card[1]
                hand.append(Card(RANK[a],SUIT[b]))
            test.hand.cards = hand[:]
            win = multi_process_eval_func_but_in_opponent_modelling(test, 6, Player(Hand(), '', 1000))[0]
            recorder = Rate_recorder()
            recorder.win = win
            print(recorder.win, hand_tmp)
            if 0.45<= recorder.win:
                hs = 'strong'
            elif 0.35 <= recorder.win < 0.45:
                hs = 'medium'
            else:
                hs = 'weak'
            for turn in actions[player]:
                bruh_action = []
                for i in actions[player][turn]:
                    bruh_action.append(('default',turn,i))
                    table = table_building(bruh_action, table, hs)
        print(datapack['gameid'])
    return(table['default'].counting_table)

if __name__ == '__main__':
    i = input('1 to crunch data, 2 to show data:\n> ')
    if int(i) == 1:
        dict = data_crunch()
        for hs in dict:
            for turn in dict[hs]:
                for action in dict[hs][turn]:
                    dict[hs][turn][action] += 1
        with open("poker_ai/ai/ml/default_data.json", 'w') as file:
            json.dump(dict, file)
    elif int(i) == 2:
        try:
            f = open("poker_ai/ai/ml/default_data.json")
        except:
            print('No file exist!')
        else:
            data = json.load(f)
            print(data)
            f.close()
    else:
        print('Error!')
