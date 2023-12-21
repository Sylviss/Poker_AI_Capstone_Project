import json

def check_validity(data):
    for hand in data:
        for turn in data[hand]:
            for check in data[hand][turn]:
                for action in data[hand][turn][check]:
                    if data[hand][turn][check][action] == 0:
                        return False
    return True

if __name__ == '__main__':
    try:
        f = open("poker_ai/ai/ml/play_data.json")
    except:
        print('No file exist!')
    else:
        data = json.load(f)
        for hand in data:
            for turn in data[hand]:
                for check in data[hand][turn]:
                    for action in data[hand][turn][check]:
                        data[hand][turn][check][action] = round(data[hand][turn][check][action])
        print(data)
        print(check_validity(data))
        f.close()
