import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 
import argparse

from src import IMU, Calibrator, QtVisualiser, PyPlotVisualiser, Vector3D, Calibrator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/data_0.csv")
    parser.add_argument("--mode", default='qt', const='qt', nargs='?', choices=['qt', 'pyplot'])

    args = parser.parse_args()

    df = pd.read_csv(args.input, sep=' ')
    sensor_data = df.to_numpy(dtype=np.float)

    calibrator = Calibrator(200)
    raw_data = get_reader_data(sensor_data)
    calibrated_data = calibrator.filter_data(raw_data) 
    
    imu = IMU()

    if args.mode == 'qt':
        visualiser = QtVisualiser()
    else:
        visualiser = PyPlotVisualiser()

    for data in calibrated_data:
        imu.update(data)
        for imu_data in imu.read_data():
            visualiser.push_data(imu_data)
    
    visualiser.start()

def get_reader_data(sensor_data):
    for data in sensor_data:
        time = data[0]
        accel = data[1:4]
        gyro = data[4:7]
        
        accel_vec = Vector3D(*accel)
        gyro_vec = Vector3D(*gyro)

        yield (time, accel_vec, gyro_vec)

if __name__ == '__main__':
    main()
