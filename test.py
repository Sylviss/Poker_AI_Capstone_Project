import json

def check_validity(data):
    a=99999
    for hand in data:
        for turn in data[hand]:
            for check in data[hand][turn]:
                for action in data[hand][turn][check]:
                    a=min(data[hand][turn][check][action],a)
    return a

def main():
    try:
        with open("poker_ai/ai/ml/default_data.json") as f:
            data = json.load(f)
            print(list(data.keys()))
    except:
        print('No file exist!')
if __name__ == '__main__':
    main()
