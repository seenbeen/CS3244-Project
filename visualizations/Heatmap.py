import matplotlib.pyplot as plt
import numpy as np

size = np.genfromtxt('positions.csv', delimiter='\t', skip_header=1, max_rows=1)
data = np.genfromtxt('positions.csv', delimiter='\t', skip_header=3)

x = data[:,0]
y = data[:,1]

#heatmap, xedges, yedges = np.histogram2d(x, y, bins=(size[0],size[1]))
#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
#extent = [0, size[0], 0, size[1]]

#plt.imshow(heatmap, extent=extent)
#plt.imshow(data, cmap='hot', extent=extent, origin='upper')
plt.hist2d(x, y, range=[[0, size[0]],[0, size[1]]], bins=[size[0]//10, size[1]//10])


#heatmap, xedges, yedges = plt.hist2d(x, y, range=[[0, size[0]],[0, size[1]]])
#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

#plt.imshow(heatmap, extent=extent)
plt.gca().invert_yaxis()
plt.show()
