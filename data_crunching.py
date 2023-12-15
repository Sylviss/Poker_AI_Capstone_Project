from poker_ai.datasets.data_extract import main
from poker_ai.poker.poker_component import Card, Hand, Player
from poker_ai.ai.eval_func import multi_process_eval_func_but_in_opponent_modelling
from poker_ai.ai.ml.opponent_modelling import Data_table, opponent_modelling, Rate_recorder, table_building

if __name__ == '__main__':
    RANK = {'2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, 'T':9, 'J':10, 'Q':11, 'K':12, 'A':13}
    SUIT = {'d':1, 'h':2, 's':3, 'c':0}
    dataset = main()[:100]
    res = []
    hands = {}
    actions = {}
    table = {'default':Data_table()}
    test = Player(Hand(), 'bruh', 1000)
    for datapack in dataset:
        for player_dict in datapack['players']:
            hands[player_dict['player_name']]=player_dict['player_hand']
            actions[player_dict['player_name']] = {i:[] for i in [0,3,4,5]}
        for i in [0,3,4,5]:
            bruh = datapack['actions'][i]
            if bruh != None:
                for bruhbruh in bruh:
                    actions[bruhbruh[0]][i].append(bruhbruh[1][0])
        for player in hands:
            hand_tmp = hands[player]
            hand = []
            for card in hand_tmp:
                a, b = card[0], card[1]
                hand.append(Card(RANK[a],SUIT[b]))
            h = Hand()
            test.hand.cards = hand[:]
            win, draw = multi_process_eval_func_but_in_opponent_modelling(test, 6, Player(Hand(), '', 1000))
            recorder = Rate_recorder()
            recorder.win = win
            print(recorder.win, hand_tmp)
            if recorder.win >= 0.5:
                hs = 'strong'
            elif 0.3 <= recorder.win < 0.5:
                hs = 'medium'
            else:
                hs = 'weak'
            for turn in actions[player]:
                bruh_action = []
                for i in actions[player][turn]:
                    bruh_action.append(('default',turn,i))
                    table = table_building(bruh_action, table, hs)
        print(datapack['gameid'])
    print(table['default'].counting_table)

