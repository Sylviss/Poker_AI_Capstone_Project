from poker_ai.ai.ml.opponent_modelling import Data_table
import json
files = ['2p_1.json','4p_1.json','6p_1.json','play_data_vu_2.json','play_data_vu_4.json']

with open('poker_ai/ai/ml/'+'2p_1.json') as f:
    datas = json.load(f)
for file in files:
    with open('poker_ai/ai/ml/'+file) as f:
        data = json.load(f)
        for hand in data:
            for turn in data[hand]:
                for check in data[hand][turn]:
                    for action in data[hand][turn][check]:
                        datas[hand][turn][check][action] += data[hand][turn][check][action]
with open('poker_ai/ai/ml/bruh.json','w') as f:
    json.dump(datas, f)

