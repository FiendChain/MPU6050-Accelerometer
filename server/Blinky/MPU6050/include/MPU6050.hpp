#pragma once
#include "i2c.h"

class MPU6050
{

public:
	template <typename T>
	struct Vector3D {
		T x, y, z;
	};

	struct SensorData {
		Vector3D<float> accel;
		Vector3D<float> gyro;
	};

public:
	static const int MAX_BUFFER_SIZE = 20;

private:
	static constexpr float m_accel_sensitivity[4] = {16384.0f, 8192.0f, 4096.0f, 2048.0f};
	// equivalent to bit shift, value >> m_accel_sensitivity[mode]
	// static constexpr uint8_t m_accel_sensitivity[4] = {14, 13, 12, 11};
	static constexpr float m_gyro_sensitivity[4] = {131.0f, 65.5f, 32.8f, 16.4f};
private:
	I2C_HandleTypeDef *m_i2c_handler;
	uint8_t m_i2c_address; // 8bit addr
	uint8_t m_buffer[MAX_BUFFER_SIZE];
	uint8_t m_accel_mode, m_gyro_mode;
public:
	MPU6050(I2C_HandleTypeDef *i2c_handler);
	void SetClockSource(uint8_t source);
	void SetAccelFullScaleRange(uint8_t mode);
	void SetGyroFullScaleRange(uint8_t mode);
	void SetSleep(bool is_sleep);
	SensorData GetSensorData();
	bool IsReady();
private:
	void ReadBytes(uint8_t reg_addr, uint8_t *buffer, uint8_t total_bytes);
	uint8_t ReadByte(uint8_t reg_addr);
	void WriteByte(uint8_t reg_addr, uint8_t value);
};
