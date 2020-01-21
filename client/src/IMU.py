from collections import deque
import numpy as np
import math

from .Vector3D import Vector3D

class IMU:
    def __init__(self):
        self.current_time = 0
        self.last_read_time = None

        self.orientation = Vector3D(0, 0, 0)
        self.unfiltered_orientation = Vector3D(0, 0, 0)
        self.low_pass_gyro_orientation = Vector3D(0, 0, 0)

        self.accel_low_pass_filter = LowPassFilter(20)
        self.gyro_low_pass_filter = LowPassFilter(100)

        self.buffer = deque([])

    # output parsed data
    def read_data(self):
        while len(self.buffer) > 0:
            yield self.buffer.popleft()

    def update(self, data):
        read_time, accel, gyro = data
        dt = self.calculate_dt(read_time)
        
        self.current_time += dt
        dt_ms = dt / 1000

        # keep track of yaw
        filtered_accel = self.accel_low_pass_filter.get_value(accel, dt_ms)
        filtered_gyro = self.gyro_low_pass_filter.get_value(gyro, dt_ms)

        self.unfiltered_orientation += gyro*dt_ms
        self.low_pass_gyro_orientation += filtered_gyro*dt_ms

        angle_accel = self.calculate_gravity_orientation(filtered_accel)
        # complementary filter
        filtered_gyro_angle = self.orientation + gyro*dt_ms 
        alpha = 0.96

        # cant compute yaw without magnetometer
        angle_accel.x = filtered_gyro_angle.x
        self.orientation = alpha*filtered_gyro_angle + (1-alpha)*angle_accel

        data = [self.current_time]
        data.extend(list(accel))
        data.extend(list(gyro))
        data.extend(list(self.orientation))
        data.extend(list(self.unfiltered_orientation))
        data.extend(list(angle_accel))
        data.extend(list(self.low_pass_gyro_orientation))
        data.extend(list(filtered_accel))
        data.extend(list(filtered_gyro))

        self.buffer.append(np.array(data))

    # can only calculate two angles from gravity sensor
    # cannot measure yaw 
    # https://i0.wp.com/www.geekmomprojects.com/wp-content/uploads/2013/04/accelerometer_angles.jpg
    def calculate_gravity_orientation(self, accel):
        # default gravity is (1, 0, 0)
        angle_rad = Vector3D()
        angle_rad.x = math.atan(-accel.y / (accel.x**2 + accel.z**2)**0.5)
        angle_rad.y = math.atan(+accel.z / (accel.x**2 + accel.y**2)**0.5)
        angle_rad.z = math.atan(-accel.y / (accel.x**2 + accel.z**2)**0.5)

        angle_deg = angle_rad * (180/math.pi)

        return angle_deg 

    def calculate_dt(self, read_time):
        if self.last_read_time is None:
            self.last_read_time = read_time

        dt = read_time - self.last_read_time
        self.last_read_time = read_time

        return dt

class LowPassFilter:
    def __init__(self, f_cutoff):
        self.w_cutoff = f_cutoff / (2*math.pi)
        self.last_y = None
    
    def get_value(self, x, dt_ms):
        alpha = dt_ms / (1/self.w_cutoff + dt_ms)
        # if high cutoff, alpha is closer to 1
        # if low cutoff, alpha is closer to 0

        if self.last_y is None:
            self.last_y = alpha*x
            return x

        # if difference is small
        y = alpha*x + (1-alpha)*self.last_y
        self.last_y = y

        return y

        
    
