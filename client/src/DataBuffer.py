from collections import deque
import numpy as np

# visualise acceleration, gyro, and estimated orientation
class DataBuffer(deque):
    def __init__(self, time_window=1.5):
        super().__init__([])
        self.time_window = time_window

    def append(self, data):
        super().append(data)
        self.truncate_data()

    def truncate_data(self):
        if len(self) == 0:
            return

        # truncate data thats past window
        last_time = self[-1][0]
        cutoff_time = last_time - (self.time_window * 1000)

        while len(self) > 0:
            entry = self[0]
            entry_time = entry[0]
            if entry_time < cutoff_time:
                self.popleft() 
            else:
                break