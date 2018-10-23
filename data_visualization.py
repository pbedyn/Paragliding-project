# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 09:23:06 2018

@author: BedynskiPa01
"""
import numpy as np

import matplotlib
import matplotlib.pyplot as plt

###############################################################################
#### plot a bar chart
def plot_bar_chart(df_data, title):
    
    fig, ax = plt.subplots()
    num_bins = 100
    mu = np.mean(df_data)
    sigma = np.std(df_data)

    n, bins, patches = ax.hist(df_data[df_data > 0], num_bins, density = 1)

    y = ((1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
    ax.plot(bins, y, '--')
    ax.set_xlabel(title)
    ax.set_ylabel('Probability density')
    ax.set_title(r'Histogram of: ' + title)
    fig.tight_layout()
    plt.show()
    

plot_bar_chart(df_t['longitude'][df_t['longitude'] > 75], "longitude")
plot_bar_chart(df_t['latitude'][df_t['latitude'] > 3], "latitude")
    

'''
======================
3D surface (color map)
======================

Demonstrates plotting a 3D surface colored with the coolwarm color map.
The surface is made opaque by using antialiased=False.

Also demonstrates using the LinearLocator and custom formatting for the
z axis tick labels.
'''
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
X = np.arange(0, 20000, 1)
Y = np.arange(0, 20000, 1)
Z = grid

# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(0, 500)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()