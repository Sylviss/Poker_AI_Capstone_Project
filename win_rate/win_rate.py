import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

# define figure and axes 
fig, ax = plt.subplots()

# create values for table:
table_data = [
    ['Bot', -1, 0, 1, 2],
    [-1, 50, 72.5, 41.5, 100],
    [0, 27.5, 50, 38, 97.5],
    [1, 58.5, 62, 50, 100],
    [2, 0, 2.5, 0, 50],
    
]

# create table 
table = ax.table(cellText=table_data, loc='center')

# modify table 

table.set_fontsize(14)
table.scale(0.5, 2)

# set cell alignment to center 
for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        table[i, j].set_text_props(ha = 'center')

# set cell color 
for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        if i == 0 or j == 0:
            table[i, j].set_facecolor('#6495ed')
        
        else:
            table[i, j].set_facecolor('#f2f2f2')

title = plt.title('Win rate (%)', fontsize = 30, weight = 'bold')
title.set_color('#ff0000')

ax.axis('off')

#display table 
plt.show()
