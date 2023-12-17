import json
from poker_ai.ai.ml.opponent_modelling import Data_table, table_counting, table_rescaling

try:
    f = open("poker_ai/ai/ml/play_data.json")
except:
    print('No file exist!')
else:
    data = json.load(f)
    print(data)
    f.close()
