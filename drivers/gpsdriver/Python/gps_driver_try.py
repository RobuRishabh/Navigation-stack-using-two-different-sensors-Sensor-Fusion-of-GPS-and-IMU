#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import utm
import serial
import sys
from gpsdriver.msg import *
from gpsdriver.msg import gps_msg

def driver():
    pub = rospy.Publisher('gps', gps_msg, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    #rate = rospy.Rate(10)
    msg = gps_msg()

    args = rospy.myargv(argv = sys.argv)
    if len(args) != 2:
        print("error")
        sys.exit(1)

    connected_port = args[1]
    serial_port = rospy.get_param('~port',connected_port)
    serial_baud = rospy.get_param('~baudrate',4800)

    ser = serial.Serial(serial_port, serial_baud, timeout = 3)

    while not rospy.is_shutdown():
        recieve = str(ser.readline())
        # recieve = recieve.decode('utf-8')

        if "$GPGGA" in str(recieve):
            data = str(recieve).split(",")
            print(data)
            utc = float(data[1])
            utc_hrs = utc//10000
            utc_mint = (utc-(utc_hrs*10000))//100
            utc_sec = (utc - (utc_hrs*10000) - (utc_mint*100))
            utc_final_secs = (utc_hrs*3600 + utc_mint*60 + utc_sec)
            utc_final_nsecs = int((utc_final_secs * (10**7)) % (10**7))


            lat = float(data[2])
            lat_DD = int(lat/100)
            lat_mm1 = float(lat) - (lat_DD * 100)
            lat_converted = float(lat_DD + lat_mm1/60)
            if data[3]=='S':
                lat_converted= lat_converted*(-1)
            
            long = float(data[4])
            long_DD = int(long / 100)
            long_mm1 = float(long) - (long_DD * 100)
            long_converted = float(long_DD + long_mm1/60)
            if data[5]=='W':
                long_converted=long_converted*(-1)
            
            alt = float(data[9])

            newlatlong = utm.from_latlon(lat_converted,long_converted)
            print(f'UTM_East, UTM_north, Zone, Letter: {newlatlong}')
            #time.sleep(1)
            #msg.header.stamp = rospy.Time.from_sec(utc_final)
            msg.header.stamp.secs = int(utc_final_secs)
            msg.header.stamp.nsecs = int(utc_final_nsecs)
            msg.header.frame_id = 'GPS1_Frame'
            msg.Latitude = lat_converted
            msg.Longitude = long_converted
            msg.Altitude = alt
            msg.UTM_easting = newlatlong[0]
            msg.UTM_northing = newlatlong[1]
            msg.Zone = newlatlong[2]
            msg.Letter = newlatlong[3]
            pub.publish(msg)
            #rate.sleep()


if __name__ == '__main__':
    try:
        driver()
    except rospy.ROSInterruptException:
        pass
