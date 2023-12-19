import json
from types import prepare_class

def check_validity(data):
    for hs in data:
        for turn in data[hs]:
            if data[hs][turn]['can only check']['call'] >= 1:
                print(hs, turn, 1, data[hs][turn]['can only check']['call'])
                print('Invalid!')
                return False
            if data[hs][turn]['can only call']['check'] >= 1:
                print(hs, turn, 2, data[hs][turn]['can only call']['check'])
                print('Invalid!')
                return False
            if data[hs][turn]["can't check or call"]['check'] >= 1:
                print(hs, turn, 3, data[hs][turn]["can't check or call"]['call'])
                print('Invalid!')
                return False
            if data[hs][turn]["can't check or call"]['call'] >= 1:
                print(hs, turn, 4, data[hs][turn]["can't check or call"]['call'])
                print('Invalid!')
                return False
            for check in data[hs][turn]:
                for action in data[hs][turn][check]:
                    if data[hs][turn][check][action] < 0:
                        print('<0','Invalid!')
                        return False
    return True

if __name__ == '__main__':
    try:
        f = open("poker_ai/ai/ml/play_data.json")
    except:
        print('No file exist!')
    else:
        data = json.load(f)
        for player in data:
            check_validity(data[player])
        for player in data:
            for hs in data[player]:
                for turn in data[player][hs]:
                    for check in data[player][hs][turn]:
                        for action in data[player][hs][turn][check]:
                            data[player][hs][turn][check][action] = int(data[player][hs][turn][check][action])
        print(data)
        f.close()
