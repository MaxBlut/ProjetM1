import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 8))

y = np.random.randint(0, 100, size=50)
x = np.random.choice(np.arange(len(y)), size=10)

line, = ax.plot(y, '-', label='line')
dot, = ax.plot(x, y[x], 'o', label='dot')

legend = plt.legend(loc='upper right')
line_legend, dot_legend = legend.get_lines()
line_legend.set_picker(True)
line_legend.set_pickradius(10)
dot_legend.set_picker(True)
dot_legend.set_pickradius(10)

graphs = {}
graphs[line_legend] = line
graphs[dot_legend] = dot


def on_pick(event):
    legend = event.artist
    isVisible = legend.get_visible()

    graphs[legend].set_visible(not isVisible)
    legend.set_visible(not isVisible)

    fig.canvas.draw()

plt.connect('pick_event', on_pick)
plt.show()