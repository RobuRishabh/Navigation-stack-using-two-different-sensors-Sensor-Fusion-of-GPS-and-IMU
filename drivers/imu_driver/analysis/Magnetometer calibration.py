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
plt.rcParams.update({'font.size': 30})
sns.set_style("dark")
sns.color_palette("viridis", as_cmap=True)

bag = bagreader('/home/rishabh/LAB4/src/imu_driver/data/data_going_in_circles.bag')
data = bag.message_by_topic('/imu')
readings = pd.read_csv(data)
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.scatter(readings['MagField.magnetic_field.x'], readings['MagField.magnetic_field.y'], marker='.', label='Raw/Uncalibrated Data')
doughnut = plt.Circle((0.1, -0.13), 0.2, fill=False, color='black')
plt.gca().add_patch(doughnut)
plt.gca().set_aspect("equal")


#CALIBRATION
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

plt.grid(color='grey', linestyle='--', linewidth=1)
plt.scatter(hard_iron_x, hard_iron_y, marker='+', label='Hard-Iron Calibrated Data', color='crimson')
doughnut = plt.Circle((0.0, 0.0), 0.2, fill=False, color='black')
plt.gca().add_patch(doughnut)
plt.gca().set_aspect("equal")
plt.title('Hard_Iron_Calibration Plot Of Magnetic Field X vs Y')
plt.xlabel('Hard_Iron_X (Guass)')
plt.ylabel('Hard_Iron_Y (Guass)')
plt.legend()
plt.show()

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
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.scatter(matrix[0], matrix[1], marker='x', label = 'Soft-Iron Calibrated', color='palevioletred')
doughnut = plt.Circle((0.0, 0.0), 0.2, fill=False, color='black')
plt.gca().add_patch(doughnut)
plt.gca().set_aspect("equal")
plt.title('Soft_Iron_Calibration Of Magnetic Field X vs Y')
plt.xlabel('Soft_Iron_X (Guass)')
plt.ylabel('Soft_Iron_Y (Guass)')
plt.legend()
plt.show()

#Find Major and Minor axis using distance formula
r = 0.2
q = 0.15
sigma = q/r
print('sigma = ', sigma)

#Scaling
matrix2 = [[1, 0], [0, sigma]]
rotate = np.matmul(matrix2, matrix)
theta = -theta
R1 = [[np.cos(theta), np.sin(theta)], [np.sin(-theta), np.cos(theta)]]
v1 = np.matmul(R1, rotate)
print(np.shape(v1))
plt.grid(color='grey', linestyle='--', linewidth=1)
plt.scatter(v1[0], v1[1], marker='x', label='Hard and Soft Iron Calibrated Data', color='indianred')
doughnut = plt.Circle((0.0, 0.0), 0.15, fill=False, color='black')
plt.gca().add_patch(doughnut)
plt.gca().set_aspect("equal")
plt.title('Final Calibrated Plot Of Magnetic Field X vs Y')
plt.xlabel('Mx (Guass)')
plt.ylabel('My (Guass)')
plt.rcParams.update({'font.size': 22})
plt.legend()
plt.show()

