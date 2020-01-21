import serial
import threading
import argparse

from src import Reader, QtVisualiser, Calibrator, IMU, DataBuffer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM11")
    parser.add_argument("--baudrate", default=1000000, type=int)
    parser.add_argument("--preview-window", default=5.0, type=float)
    parser.add_argument("--calibration-samples", default=500, type=int)

    args = parser.parse_args()

    com = serial.Serial(port=args.port, baudrate=args.baudrate)
    reader = Reader(com)

    buffer = DataBuffer(time_window=args.preview_window)
    visualiser = QtVisualiser(buffer)
    calibrator = Calibrator(args.calibration_samples)

    imu = IMU()

    def data_listener():
        raw_readings = reader.get_readings()
        calibrated_readings = calibrator.filter_data(raw_readings)

        for i, data in enumerate(calibrated_readings):
            imu.update(data)

            for imu_data in imu.read_data():
                visualiser.push_data(imu_data)

    data_listener_thread = threading.Thread(target=data_listener)

    try:
        reader.start()
        data_listener_thread.start()
        # this blocks
        visualiser.start_threaded()
    except KeyboardInterrupt as ex:
        print(ex)
    finally:
        reader.stop()
        data_listener_thread.join()

if __name__ == '__main__':
    main()