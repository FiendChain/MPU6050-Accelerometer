import time
import struct
import threading

from collections import deque

from .Vector3D import Vector3D

class Reader:
    def __init__(self, com):
        self.com = com
        self.running = False

        self.buffered_data = deque([])

        self.serial_thread = threading.Thread(target=self.start_read)

    def get_readings(self):
        while self.running:
            while len(self.buffered_data) > 0:
                yield self.buffered_data.popleft()
            time.sleep(0.001)

    def start(self):
        self.running = True
        self.serial_thread.start()

    def stop(self):
        self.running = False
        self.serial_thread.join()

    def start_read(self):
        data_buffer = []
        packet_format = ">HLffffff"
        packet_size = struct.calcsize(packet_format)



        header_id = 0xba41

        try:
            while self.com.isOpen() and self.running:
                data = self.com.read_all()        
                data_buffer.extend(data)

                while len(data_buffer) >= packet_size:
                    packet = struct.unpack(packet_format, bytes(data_buffer[:packet_size]))
                    header, read_time, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = packet
                    # invalid header, move into next byte
                    if header != header_id:
                        data_buffer = data_buffer[1:]
                        continue

                    data_buffer = data_buffer[packet_size:]
                    
                    accel = Vector3D(accel_x, accel_y, accel_z)
                    gyro = Vector3D(gyro_x, gyro_y, gyro_z)

                    data = [read_time, accel, gyro]

                    self.buffered_data.append(data)

                if not data:
                    time.sleep(0.001)
        finally:
            self.running = False