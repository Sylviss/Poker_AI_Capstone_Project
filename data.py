import json
with open('poker_ai/ai/ml/play_data_vu_4.json') as f:
    data = json.load(f)
    for hand in data:
        for turn in data[hand]:
            for check in data[hand][turn]:
                for action in data[hand][turn][check]:
                    data[hand][turn][check][action] = round(data[hand][turn][check][action]) + 0.0000001
    f.close()
with open('poker_ai/ai/ml/play_data_vu_4.json','w') as f:
    json.dump(data, f)
    f.close()
