import numpy as np
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from .DataBuffer import DataBuffer

class QtVisualiser:
    def __init__(self, buffer=[]):
        self.buffer = buffer

        self.window = pg.GraphicsWindow() 
        self.window.setWindowTitle("Gyro data")

        self.subplots = []

        plot = self.window.addPlot(title="Accelerometer")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Linear Acceleration (g)')
        self.subplots.append(Subplot(plot))

        plot = self.window.addPlot(title="Gyroscope")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Angular velocity (deg/s)')
        self.subplots.append(Subplot(plot))

        plot = self.window.addPlot(title="Filtered Orientation")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Orientation (deg)')
        self.subplots.append(Subplot(plot))

        self.window.nextRow()

        plot = self.window.addPlot(title="Unfiltered Orientation")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Orientation (deg)')
        self.subplots.append(Subplot(plot))

        plot = self.window.addPlot(title="Accelerometer Orientation")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Orientation (deg)')
        self.subplots.append(Subplot(plot))

        plot = self.window.addPlot(title="Low pass gyro-orientation")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Orientation (deg)')
        self.subplots.append(Subplot(plot))

        self.window.nextRow()

        plot = self.window.addPlot(title="Low pass accelerometer")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Linear acceleration (ms^-2)')
        self.subplots.append(Subplot(plot))

        plot = self.window.addPlot(title="Low pass gyroscope")
        plot.setLabel('bottom', 'Time (ms)')
        plot.setLabel('left', 'Angular velocity (deg/s)')
        self.subplots.append(Subplot(plot))

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.render)


    def start_threaded(self):
        self.timer.start(int(1000/60))
        self.start()
    
    def start(self):
        self.render()
        if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
            pg.QtGui.QApplication.exec_()


    def render(self):
        if len(self.buffer) == 0:
            return

        data = np.array(self.buffer)

        x = data[:,0] # x data
        data_format = [
            3, 3, 3, # accel, gyro, filtered orientation 
            3, 3, 3, # unfiltered gyro orientation, gravity orientation, low pass gyro orientation
            3, 3     # low pass accel, low pass gyro
        ]

        i = 1
        for plot, width in zip(self.subplots, data_format):
            y = data[:,i:(i+width)]
            plot.update_data(x, y)
            i += width

    def push_data(self, data):
        self.buffer.append(data)

class Subplot:
    def __init__(self, plot, total_axes=3):
        self.plot = plot
        self.plot.showGrid(x=True, y=True, alpha=1.0)
        self.plot.setClipToView(True)
        self.total_axes = total_axes

        curve_name = ['x', 'y', 'z']
        self.legend = self.plot.addLegend()
        self.curves = []

        for axis in range(total_axes):
            curve = plot.plot(pen=(axis, self.total_axes)) # auto create pen
            self.curves.append(curve)
            self.legend.addItem(curve, curve_name[axis])



    def update_data(self, x, y):
        for axis in range(self.total_axes):
            curve = self.curves[axis]
            sub_y = y[:,axis]
            curve.setData(x, sub_y)
