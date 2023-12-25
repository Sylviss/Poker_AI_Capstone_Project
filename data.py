import json
files = ['bruh.json', 'bruh_4.json', 'bruh_6.json']
datas = {2:{}, 4:{}, 6:{}}
for i in range(len(files)):
    with open('poker_ai/ai/ml/'+files[i]) as file:
        data = json.load(file)
        if i == 0:
            datas[2] = data
        elif i == 1:
            datas[4] = data
        elif i == 2:
            datas[6] = data
        file.close()
with open('poker_ai/ai/ml/default_data.json', 'w') as file:
    json.dump(datas, file)
    file.close()
