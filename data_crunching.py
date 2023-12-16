import json
from poker_ai.datasets.data_extract import main
from poker_ai.poker.poker_component import Card, Hand, Player
from poker_ai.ai.eval_func import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.ai.ml.opponent_modelling import Data_table, opponent_modelling, Rate_recorder, table_building

def data_crunch():
    RANK = {'2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, 'T':9, 'J':10, 'Q':11, 'K':12, 'A':13}
    SUIT = {'d':1, 'h':2, 's':3, 'c':0}
    ACTIONS = {1:8, 2:1, 3:2, 4:4, 5:7}
    dataset = main()[0:100]
    hands = {}
    actions = {}
    table = {'default':Data_table()}
    test = Player(Hand(), 'bruh', 4000)
    dealer = Player(Hand(), 'board', 4000)
    for datapack in dataset:
        for player_dict in datapack['players']:
            hands[player_dict['player_name']]=player_dict['player_hand']
        for turn in datapack['actions']:
            if datapack['actions'][turn] == None:
                continue
            hand_tmp = hands['Pluribus']
            hand = []
            board = []
            for card in hand_tmp:
                a, b = card[0], card[1]
                hand.append(Card(RANK[a],SUIT[b]))
            for card in datapack['board']:
                a, b = card[0], card[1]
                board.append(Card(RANK[a],SUIT[b]))
            test.hand.cards = hand[:]
            dealer.hand.cards = board[:turn]
            win, draw = multi_process_eval_func_but_in_opponent_modelling(test, 6, dealer)
            recorder = Rate_recorder()
            recorder.win = win
            if 0.45<= recorder.win:
                hs = 'strong'
            elif 0.35 <= recorder.win < 0.45:
                hs = 'medium'
            else:
                hs = 'weak'
            bruh_action = []
            for action in datapack['actions'][turn]:
                if action[0] == 'Pluribus':
                    continue
                bruh_action.append(('default',turn,ACTIONS[action[1][0]]))
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
