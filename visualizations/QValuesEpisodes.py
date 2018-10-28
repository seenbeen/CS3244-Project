import matplotlib.pyplot as plt
import numpy as np

data = np.genfromtxt('averageQValuesInEpochs.csv', delimiter='\t', skip_header=1)

qValues = data[:,0]
episodes = data[:,1]

plt.plot(episodes, qValues)
plt.title("Average Maximum QValues Over Time")
plt.xlim(left=0, right=len(data))
plt.xlabel("Training Episodes")
plt.ylabel("Average QValue per Episode")
plt.show()