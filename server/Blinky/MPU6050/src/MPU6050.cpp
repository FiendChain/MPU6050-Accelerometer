/*
 * MPU6050.cpp
 *
 *  Created on: Jan 19, 2020
 *      Author: acidi
 */

#include "MPU6050.hpp"
#include "i2c.h"

// redundant declaration for c++14
constexpr float MPU6050::m_accel_sensitivity[4];
constexpr float MPU6050::m_gyro_sensitivity[4];

MPU6050::MPU6050(I2C_HandleTypeDef *i2c_handler)
	: m_i2c_handler(i2c_handler),
	  m_i2c_address(0x68 << 1),
	  m_buffer{0},
	  m_accel_mode(0),
	  m_gyro_mode(0)
{
	SetClockSource(0x00);
	SetAccelFullScaleRange(0x03);
	SetGyroFullScaleRange(0x03);
	SetSleep(false);
}

void MPU6050::SetClockSource(uint8_t source) {
	const uint8_t reg_addr = 0x6b;
	uint8_t data = ReadByte(reg_addr);
	data = (data & 0xf8) | (data & 0x07);
	WriteByte(reg_addr, data);
}

void MPU6050::SetAccelFullScaleRange(uint8_t mode) {
	// 0 = 2g
	// 1 = 4g
	// 2 = 8g
	// 3 = 16g
	mode = mode & 0x03;
	m_accel_mode = mode;
	const uint8_t reg_addr = 0x1c;
	uint8_t data = ReadByte(reg_addr);
	data = (data & 0xE7) | (mode << 3);
	WriteByte(reg_addr, data);
}

void MPU6050::SetGyroFullScaleRange(uint8_t mode) {
	// 0 = 250 deg/s
	// 1 = 500 deg/s
	// 2 = 1000 deg/s
	// 3 = 2000 deg/s
	mode = mode & 0x03;
	m_gyro_mode = mode;
	const uint8_t reg_addr = 0x1b;
	uint8_t data = ReadByte(reg_addr);
	data = (data & 0xE7) | (mode << 3);
	WriteByte(reg_addr, data);
}

void MPU6050::SetSleep(bool is_sleep) {
	const uint8_t reg_addr = 0x6b;
	uint8_t data = ReadByte(reg_addr);
	if (is_sleep) data |=  (1 << 6);
	else		  data &= ~(1 << 6);
	WriteByte(reg_addr, data);
}

bool MPU6050::IsReady() {
	uint8_t data = ReadByte(0x3a);
	if ((data & (1u << 0)) != 0u) {
		return true;
	}
	return false;
}

MPU6050::SensorData MPU6050::GetSensorData() {
	const uint8_t start_reg_addr = 0x3b;
	uint8_t buffer[14] = {0};
	ReadBytes(start_reg_addr, buffer, sizeof(buffer));

	float accel_sensitivity = MPU6050::m_accel_sensitivity[m_accel_mode];
	float gyro_sensitivity = MPU6050::m_gyro_sensitivity[m_gyro_mode];

	Vector3D<int16_t> accel, gyro;
	SensorData sensor_data;

	accel.x = (buffer[0] << 8) | (buffer[1]);
	accel.y = (buffer[2] << 8) | (buffer[3]);
	accel.z = (buffer[4] << 8) | (buffer[5]);

	gyro.x = (buffer[8] << 8) | (buffer[9]);
	gyro.y = (buffer[10] << 8) | (buffer[11]);
	gyro.z = (buffer[12] << 8) | (buffer[13]);

	sensor_data.accel.x = (float)(accel.x) / accel_sensitivity;
	sensor_data.accel.y = (float)(accel.y) / accel_sensitivity;
	sensor_data.accel.z = (float)(accel.z) / accel_sensitivity;


	sensor_data.gyro.x = (float)(gyro.x) / gyro_sensitivity;
	sensor_data.gyro.y = (float)(gyro.y) / gyro_sensitivity;
	sensor_data.gyro.z = (float)(gyro.z) / gyro_sensitivity;

	return sensor_data;
}

void MPU6050::ReadBytes(uint8_t reg_addr, uint8_t *buffer, uint8_t total_bytes) {
	HAL_I2C_Master_Transmit(m_i2c_handler, m_i2c_address, &reg_addr, 1, 10);
	HAL_I2C_Master_Receive(m_i2c_handler, m_i2c_address, buffer, total_bytes, 10);
}

uint8_t MPU6050::ReadByte(uint8_t reg_addr) {
	uint8_t value;
	ReadBytes(reg_addr, &value, 1);
	return value;
}

void MPU6050::WriteByte(uint8_t reg_addr, uint8_t value) {
	uint8_t buffer[2] = {reg_addr, value};
	HAL_I2C_Master_Transmit(m_i2c_handler, m_i2c_address, buffer, 2, 10);
}
