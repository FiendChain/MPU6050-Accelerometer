from matplotlib import pyplot as plt 
import numpy as np
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import threading
import time

from .DataBuffer import DataBuffer

# Visualiser using matplotlib - Very slow
class PyPlotVisualiser:
    def __init__(self, buffer=[]):
        self.buffer = buffer
        self.figure = AccelFigure()
    
    def start_threaded(self):
        if len(self.buffer) == 0:
            return

        update_time = 1000/60
        while True:
            self.redraw()
            time.sleep(update_time)
    
    def start(self):
        self.redraw()
        self.figure.show()
        plt.show()
    
    def redraw(self):
        self.figure.update(self.buffer)
        self.figure.redraw()
    
    def push_data(self, data):
        self.buffer.append(data)

class AccelFigure:
    def __init__(self):
        self.figure = plt.figure()
        x = []
        y = []

        subplot = self.figure.add_subplot(131)
        subplot.set_ylim([-15, 15])
        subplot.set_title("Linear acceleration")
        subplot.set_ylabel("ms-2")
        subplot.set_xlabel("ms")
        subplot.yaxis.set_minor_locator(AutoMinorLocator(5))
        subplot.grid(which='minor', linestyle=":")
        subplot.grid(which="major", linestyle="--")

        self.accel_subplot = Subplot(subplot)

        subplot = self.figure.add_subplot(132)
        subplot.set_ylim([-250, 250])
        subplot.set_title("Angular velocity")
        subplot.set_ylabel("deg/s")
        subplot.set_xlabel("ms")
        subplot.yaxis.set_minor_locator(AutoMinorLocator(10))
        subplot.grid(which='minor', linestyle=":")
        subplot.grid(which="major", linestyle="--")

        self.gyro_subplot = Subplot(subplot)

        subplot = self.figure.add_subplot(133)
        subplot.set_ylim([-360, 360])
        subplot.set_title("Orientation")
        subplot.set_ylabel("deg")
        subplot.set_xlabel("ms")
        subplot.yaxis.set_minor_locator(AutoMinorLocator(10))
        subplot.grid(which='minor', linestyle=":")
        subplot.grid(which="major", linestyle="--")

        self.orientation_subplot = Subplot(subplot)

    def show(self):
        self.figure.show()

    def update(self, data):
        self.update_data(data)
    
    def redraw(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events() 
    
    def update_data(self, data):
        data = np.array(data)
        x = data[:,0]

        accel_data = data[:,1:4]
        gyro_data = data[:,4:7]
        orientation_data = data[:,7:10]

        self.accel_subplot.update_data(x, accel_data)
        self.gyro_subplot.update_data(x, gyro_data)
        self.orientation_subplot.update_data(x, orientation_data)


class Subplot:
    def __init__(self, subplot, total_axes=3):
        self.subplot = subplot
        self.total_axes = 3
        self.lines = [self.subplot.plot([], [])[0] for _ in range(3)]
    
    def update_data(self, x, y):
        if len(x) == 0:
            return

        xlim = (x[0], x[-1])
        self.subplot.set_xlim(xlim)

        for axis in range(self.total_axes):
            line = self.lines[axis]
            sub_y = y[:,axis]
            line.set_xdata(x)
            line.set_ydata(sub_y)

        

