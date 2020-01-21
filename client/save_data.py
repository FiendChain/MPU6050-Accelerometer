import serial
import threading
import csv
import argparse
import numpy as np

from src import Reader, QtVisualiser, Calibrator, IMU, DataBuffer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM11")
    parser.add_argument("--baudrate", default=1000000, type=int)
    parser.add_argument("--output", default="data/data.csv")
    parser.add_argument("--sampling-time", default=10.0, type=float)
    parser.add_argument("--preview-window", default=5.0, type=float)

    args = parser.parse_args()

    com = serial.Serial(port=args.port, baudrate=args.baudrate)
    reader = Reader(com)

    buffer = DataBuffer(time_window=args.preview_window)
    visualiser = QtVisualiser(buffer)
    calibrator = Calibrator(200)

    imu = IMU()

    fp = open(args.output, "w+")
    fp.write("time accel_x accel_y accel_z gyro_x gyro_y gyro_z\n")

    import time

    def reading_interceptor(raw_readings):
        for data in raw_readings:
            dt, accel, gyro = data
            fp.write(f"{dt} {accel:+f} {gyro:+f}\n")
            yield data

    def start_data_ingest():
        raw_readings = reader.get_readings()
        raw_readings = reading_interceptor(raw_readings)
        calibrated_readings = calibrator.filter_data(raw_readings)

        for data in calibrated_readings:
            imu.update(data)

            for imu_data in imu.read_data():
                visualiser.push_data(imu_data)

            if imu.current_time/1000 > args.sampling_time:
                break

        print(f"Finished reading {imu.current_time/1000:.02f} seconds of data!")


    data_ingester = threading.Thread(target=start_data_ingest)

    try:
        print("Starting")
        reader.start()
        data_ingester.start()
        # this blocks
        visualiser.start_threaded()
    except KeyboardInterrupt as ex:
        print(ex)
    finally:
        print("Writing data")            
        reader.stop()
        data_ingester.join()
        fp.close()

if __name__ == '__main__':
    main()