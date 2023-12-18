import matplotlib.pyplot as plt 

bot_1 = [0.49, 0.485, 0.48, 0.5, 0.48, 0.495, 0.59, 0.56, 0.445]
bot_minus1 = [0.51, 0.515, 0.52, 0.5, 0.52, 0.505, 0.41, 0.44, 0.555]

update_weight = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']

plt.plot(update_weight, bot_minus1, label='Win rate of bot -1', marker = 'o', markerfacecolor = 'blue')
plt.plot(update_weight, bot_1, label='Win rate of bot 1', marker = 'o', markerfacecolor = 'red')

plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)

plt.xlabel('UPDATE WEIGHT')
plt.ylabel('WIN RATE')

plt.title('WIN RATE COMPARISION')
plt.legend()

plt.show()
