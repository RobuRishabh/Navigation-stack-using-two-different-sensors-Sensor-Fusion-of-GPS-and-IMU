import bagpy
from bagpy import bagreader
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
sns.set_theme()
sns.set(font_scale=3)
plt.rcParams.update({'font.size': 40})

bag = bagreader('/home/rishabh/LAB4/src/gpsdriver/data/data_driving.bag')
#bag.topic_table
data = bag.message_by_topic('/gps')
readings = pd.read_csv(data)
readings['UTM_easting'] = readings['UTM_easting'] - readings['UTM_easting'].min()
readings['UTM_northing'] = readings['UTM_northing'] - readings['UTM_northing'].min()
print(readings[['UTM_easting', 'UTM_northing']])
print(readings)
readings[['UTM_easting','UTM_northing']].plot()
plt.show()
# fig, ax = bagpy.create_fig(1)
sns.scatterplot(x = 'UTM_easting', y = 'UTM_northing', data = readings, s= 50, label = 'UTM_easting VS UTM_northing')
plt.xlabel('UTM_easting (meters)')
plt.ylabel('UTM_northing (meters)')
plt.title('UTM_easting vs UTM_northing')
plt.show()
