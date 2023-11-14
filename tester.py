from collections import defaultdict
from poker_ai.poker.play import game, INDICATOR, STOP
import bext

d = defaultdict(lambda: 0)
for i in range(50):
    d[game(2,100,1,2)] += 1

bext.clear()
for key in d:
    print(f'{key.model}: {d[key]}')
