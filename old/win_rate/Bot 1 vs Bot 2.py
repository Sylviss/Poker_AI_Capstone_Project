import matplotlib.pyplot as plt 

bot_1 = [0.505, 0.55, 0.45, 0.39, 0.53, 0.57, 0.51, 0.45, 0.51, 0.48, 0.46]
bot_2 = [0.495, 0.45, 0.55, 0.61, 0.47, 0.43, 0.49, 0.55, 0.49, 0.52, 0.54]

ucb1_constant = ['1', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2']

plt.plot(ucb1_constant, bot_1, label='Win rate of bot 1', marker = 'o', markerfacecolor = 'blue')
plt.plot(ucb1_constant, bot_2, label='Win rate of bot 2', marker = 'o', markerfacecolor = 'red')

plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)

plt.xlabel('UCB1_CONSTANT')
plt.ylabel('WIN RATE')

plt.title('WIN RATE COMPARISION')
plt.legend()

plt.show()
