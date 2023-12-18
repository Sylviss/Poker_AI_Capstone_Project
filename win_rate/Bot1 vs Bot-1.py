import matplotlib.pyplot as plt 

bot_1 = [0.46, 0.5, 0.62, 0.56, 0.56, 0.49, 0.53, 0.55, 0.6]
bot_minus1 = [0.54, 0.5, 0.38, 0.44, 0.44, 0.51, 0.47, 0.45, 0.4]

update_weight = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']

plt.plot(update_weight, bot_minus1, label='Win rate of bot -1', marker = 'o', markerfacecolor = 'blue')
plt.plot(update_weight, bot_1, label='Win rate of bot 1', marker = 'o', markerfacecolor = 'red')

plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)

plt.xlabel('UPDATE WEIGHT')
plt.ylabel('WIN RATE')

plt.title('WIN RATE COMPARISION')
plt.legend()

plt.show()
