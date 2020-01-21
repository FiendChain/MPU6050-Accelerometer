from .Vector3D import Vector3D

class Calibrator:
    def __init__(self, total_samples=200):
        self.accel_offset = Vector3D(0, 0, 0)
        self.gyro_offset = Vector3D(0, 0, 0)

        self.reference_accel = Vector3D(1, 0, 0)
        self.reference_gyro = Vector3D(0, 0, 0)

        self.total_samples = 200
        self.completed_samples = 0
        self.is_finished = False

    def filter_data(self, data):
        for d in data:
            read_time, accel, gyro = d
            if self.is_finished:
                # yield (read_time, accel, gyro-self.gyro_offset)
                yield (read_time, accel-self.accel_offset, gyro-self.gyro_offset)
            else:
                self.on_data(d)

    def on_data(self, data):
        _, accel, gyro, = data
        self.accel_offset += accel
        self.gyro_offset += gyro
        self.completed_samples += 1

        if self.completed_samples >= self.total_samples:
            self.accel_offset /= self.completed_samples
            self.gyro_offset /= self.completed_samples

            # calibrated = raw - error
            # error = raw - calibrated 
            # calibrated = true reference
            self.accel_offset -= self.reference_accel
            self.gyro_offset -=  self.reference_gyro

            self.is_finished = True
