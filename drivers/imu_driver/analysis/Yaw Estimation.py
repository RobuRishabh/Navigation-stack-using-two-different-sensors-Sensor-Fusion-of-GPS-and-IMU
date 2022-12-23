import bagpy
import math
import csv
import time
import statistics
from bagpy import bagreader
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from quaternion import quaternion, from_rotation_vector, rotate_vectors
import scipy.integrate as integrate
from scipy.signal import butter
from scipy import signal

sns.set_style("dark")
sns.color_palette("viridis", as_cmap=True)
plt.rcParams.update({'font.size': 30})

bag = bagreader('/home/rishabh/LAB4/src/imu_driver/data/data_driving.bag')
data = bag.message_by_topic('/imu')
readings = pd.read_csv(data)
# plt.grid(color='grey', linestyle='--', linewidth=1)
# plt.scatter(readings['MagField.magnetic_field.x'], readings['MagField.magnetic_field.y'], marker='.', label='Raw/Uncalibrated Data')
# doughnut = plt.Circle((0.1, -0.13), 0.2, fill=False, color='black')
# plt.gca().add_patch(doughnut)
# plt.gca().set_aspect("equal")


# CALIBRATION
min_x = min(readings['MagField.magnetic_field.x'])
max_x = max(readings['MagField.magnetic_field.x'])
min_y = min(readings['MagField.magnetic_field.y'])
max_y = max(readings['MagField.magnetic_field.y'])

# HARD-IRON CALIBRATION
x_axis_Offset = (min_x + max_x)/2.0
y_axis_Offset = (min_y + max_y)/2.0
print("hard-iron x_axis_Offset=", x_axis_Offset)
print("hard-iron y_axis_Offset=", y_axis_Offset)
hard_iron_x = []
p = hard_iron_x.extend((readings['MagField.magnetic_field.x']-x_axis_Offset))
hard_iron_y = []
q = hard_iron_y.extend((readings['MagField.magnetic_field.y']-y_axis_Offset))

# plt.grid(color='grey', linestyle='--', linewidth=1)
# plt.scatter(hard_iron_x, hard_iron_y, marker='+', label='Hard-Iron Calibrated Data', color='crimson')
# doughnut = plt.Circle((0.0, 0.0), 0.2, fill=False, color='black')
# plt.gca().add_patch(doughnut)
# plt.gca().set_aspect("equal")
# plt.title('Hard_Iron_Calibration Plot Of Magnetic Field X vs Y')
# plt.xlabel('Hard_Iron_X (Guass)')
# plt.ylabel('Hard_Iron_Y (Guass)')
# plt.legend()
# plt.show()

X_major = float(hard_iron_x[2000])
Y_major = float(hard_iron_y[2000])

# SOFT-IRON CALIBRATION
radius = math.sqrt((X_major**2) + (Y_major**2))
print('radius = ', radius)
theta = np.arcsin((Y_major/radius))
print('theta = ', theta)

R = [[np.cos(theta), np.sin(theta)], [np.sin(-theta), np.cos(theta)]]
v = [hard_iron_x, hard_iron_y]

matrix = np.matmul(R, v)
print(np.shape(matrix))
# plt.grid(color='grey', linestyle='--', linewidth=1)
# plt.scatter(matrix[0], matrix[1], marker='x', label = 'Soft-Iron Calibrated', color='palevioletred')
# doughnut = plt.Circle((0.0, 0.0), 0.2, fill=False, color='black')
# plt.gca().add_patch(doughnut)
# plt.gca().set_aspect("equal")
# plt.title('Soft_Iron_Calibration Of Magnetic Field X vs Y')
# plt.xlabel('Soft_Iron_X (Guass)')
# plt.ylabel('Soft_Iron_Y (Guass)')
# plt.legend()
# plt.show()

# Find Major and Minor axis using distance formula
r = 0.2
q = 0.15
sigma = q/r
print('sigma = ', sigma)

# Scaling
matrix2 = [[1, 0], [0, sigma]]
rotate = np.matmul(matrix2, matrix)
theta = -theta
R1 = [[np.cos(theta), np.sin(theta)], [np.sin(-theta), np.cos(theta)]]
v1 = np.matmul(R1, rotate)
v1 = np.expand_dims(v1, axis=0)
# plt.grid(color='grey', linestyle='--', linewidth=1)
# plt.scatter(v1[:, 0], v1[:, 1], marker='x', label='Hard and Soft Iron Calibrated Data', color='indianred')
# doughnut = plt.Circle((0.0, 0.0), 0.15, fill=False, color='black')
# plt.gca().add_patch(doughnut)
# plt.gca().set_aspect("equal")
# plt.title('Final Calibrated Plot Of Magnetic Field X vs Y')
# plt.xlabel('Mx (Guass)')
# plt.ylabel('My (Guass)')
# plt.legend()
# plt.show()


# YAW CALCULATION
w = readings['IMU.orientation.w']
x = readings['IMU.orientation.x']
y = readings['IMU.orientation.y']
z = readings['IMU.orientation.z']

# Euler from Quaternion(x, y, z, w):
t0 = +2.0 * (w * x + y * z)
t1 = +1.0 - 2.0 * (x * x + y * y)
roll_x = np.arctan2(t0, t1)

t2 = +2.0 * (w * y - z * x)
pitch_y = np.arcsin(t2)

t3 = +2.0 * (w * z + x * y)
t4 = +1.0 - 2.0 * (y * y + z * z)
yaw_z = np.arctan2(t3, t4)

roll = roll_x
print('roll', roll)
pitch = pitch_y
yaw = yaw_z

print('v1', v1, v1.shape)
mag_x = v1[:, 0]
mag_y = v1[:, 1]
print('mag_x', mag_x)
print('mag_y', mag_y)
mag_z1 = readings['MagField.magnetic_field.z']
data_x = readings['MagField.magnetic_field.x']
data_y = readings['MagField.magnetic_field.y']
data_z = readings['MagField.magnetic_field.z']
print('data_x', data_x)
print('mag_z1', mag_z1)
mag_z2 = mag_z1.to_numpy()
mag_z = np.reshape(mag_z2, (1, 35952))

# YAW calculation with calibrated data
xa = mag_z*list(np.sin(roll))
xb = mag_y*list(np.cos(roll))
X = xa - xb
ya = mag_x*list(np.cos(pitch))
yb = mag_y*list(np.sin(pitch)*np.sin(roll))
yc = mag_z*list(np.sin(pitch)*np.cos(roll))

Y = ya+yb+yc
calibrated_yaw = np.arctan2(X, Y)
yaw_cal = np.unwrap(calibrated_yaw)
yaw_cmax = max(yaw_cal)
final_cal_yaw = pd.Series(yaw_cmax)
final_cal_yaw = final_cal_yaw * (180 / np.pi)


# YAW calculation with non_calibrated data
xra = data_z*list(np.sin(roll))
xrb = data_y*list(np.cos(roll))

raw_X = xra - xrb
yra = data_x*list(np.cos(pitch))
yrb = data_y*list(np.sin(pitch)*np.sin(roll))
yrc = data_z*list(np.sin(pitch)*np.cos(roll))

yra = yra.squeeze()
yrb = yrb.squeeze()
yrc = yrc.squeeze()

raw_Y = yra + yrb + yrc
raw_X = raw_X.squeeze()

print('raw_X', raw_X)
print('raw_Y', raw_Y)

cal_raw_yaw = np.arctan2(raw_X, raw_Y)
cal_raw_yaw1 = np.unwrap(cal_raw_yaw)
final_cal_raw_yaw = pd.Series(cal_raw_yaw)
final_cal_raw_yaw = final_cal_raw_yaw * (180 / np.pi)

# Integration
gyro_int = integrate.cumtrapz(readings['IMU.angular_velocity.z'], initial=0)
gyro_int_wrap = np.unwrap(gyro_int)
plt.figure(figsize = (16,8))
plt.plot(gyro_int, label='Gyro Integrated Yaw', c='palevioletred')
plt.plot(final_cal_yaw, label='Calibrated Yaw')
plt.plot(final_cal_raw_yaw, label='Raw Yaw', c='lightseagreen')
plt.legend(loc='upper right', fontsize='x-large')
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.title('Estimation of Yaw for Magnetometer')
plt.xlabel('Samples @ 40Hz')
plt.ylabel('Yaw (degrees)')
plt.show()


# Filteration
lpf = signal.filtfilt(*butter(3, 0.1, "lowpass",fs = 40, analog=False), final_cal_yaw)
hpf = signal.filtfilt(*butter(3, 0.0001, 'highpass', fs = 40, analog=False), gyro_int)
#print(lpf[0]/10+hpf[0]/10)
plt.figure(figsize = (16,8))
plt.plot(lpf, label='LPF Calibrated Yaw')
plt.legend(loc='upper right', fontsize='x-large')
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.plot(hpf, label = 'HPF Gyro Yaw', c='seagreen')
plt.legend(loc='upper right', fontsize='x-large')
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.title('LPF for Magnetic Yaw and HPF for Gyro Yaw')
plt.xlabel('Samples @ 40Hz')
plt.ylabel('Yaw (degrees)')
plt.show()

#Original Yaw V/S Calibrated Yaw
alpha = 0.75
omega = readings['IMU.angular_velocity.z']
yaw_filtered = []
yaw_filtered = np.append(yaw_filtered,0)
for i in range(35951):
  j = i+1
  yaw_filtered = np.append(yaw_filtered, alpha*(yaw_filtered[i] + hpf[j]*0.05) + ((1-alpha)*lpf[j]))
# lpf1 = 1 - hpf1
# yaw_filtered = (hpf1*hpf) + (lpf1*lpf)
plt.figure(figsize=(16, 8))
plt.plot(yaw_filtered, label='Complementary Filter')
plt.plot(yaw_z*200, label='Yaw computed by IMU')
plt.legend(loc='lower right', fontsize='x-large')
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.xlabel('Samples @ 40 Hz')
plt.ylabel('Yaw (degrees)')
plt.title('IMU Yaw vs Complementary Filter Yaw')
plt.show()


#LPF for Yaw v/s HPF gor gyro v/x Complementary Yaw
plt.figure(figsize = (16,8))
plt.plot(lpf, label='LPF Calibrated Yaw',c= 'teal')
plt.legend(loc = "upper right")
plt.plot(hpf, label = 'HPF Gyro Yaw')
plt.plot(yaw_filtered, label='Complementary Filter',c= 'crimson')
plt.legend(loc='upper right', fontsize='x-large')
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.legend(loc="upper right")
plt.xlabel('Samples @ 40Hz')
plt.ylabel('Yaw (degrees)')
plt.title('LPF for Magnetic Yaw V/S HPF for Gyro Yaw V/S  Complimentary Yaw')
plt.show()

