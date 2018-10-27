import csv
import matplotlib.pyplot as plt
import numpy as np

data = np.genfromtxt('totalRewardsInEpochs.csv', delimiter='\t', skip_header=1, dtype=None)

print(np.array(data))
rewards = data[:,0]
episodes = data[:,1]

plt.plot(episodes, rewards)
plt.title("Total Rewards Over Time")
plt.xlim(left=0, right=len(data))
plt.xlabel("Training Episodes")
plt.ylabel("Total Reward per Episode")
plt.show()