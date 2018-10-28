import matplotlib.pyplot as plt
import numpy as np

# Import data from two separate sources and plot them on the same graph
# Fill in appropriate imports and reverse coordinates if needed

data1 = np.genfromtxt('data1.csv', delimiter='\t', skip_header=1)
data2 = np.genfromtxt('data2.csv', delimiter='\t', skip_header=1)

x1 = data1[:,0]
y1 = data1[:,1]

x2 = data2[:,0]
y2 = data2[:,1]

plt.plot(x1, y1, color='green')
plt.plot(x2, y2, color='red')
plt.xlim(left=0, right=max(len(data1), len(data2)))
plt.show()