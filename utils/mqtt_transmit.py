import paho.mqtt.client as mqtt
import time
import json
import csv
import numpy as np

def on_connect(client, userdata, flags,rc):
    print("connected with result code: "+str(rc))
    client.subscribe("dev/test")


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def read_csv_data(name):
    with open(name,newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        gps_lon = list()
        gps_lat = list()

        for row in csv_reader:
            gps_lon.append(row[0])
            gps_lat.append(row[1])

            if row[0] == '<--EOF-->':
                break

    gps_lat = np.array(gps_lat)
    gps_lon = np.array(gps_lon)
    return gps_lon, gps_lat


count = 0
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883,60)
client.loop_start()

status = {
    'connected': True
}
path = 'ts/ams/temperature/2'
lon_path ='ts/gps/longitudinal'
lat_path ='ts/gps/lateral'
file_path = 'gps_AIH.csv'

gps_lon, gps_lat = read_csv_data(file_path)

while True:
    for i in range(len(gps_lon)):
        client.publish(lon_path, gps_lon[i])
        client.publish(lat_path, gps_lat[i])
        time.sleep(0.1)
    """
    status['connected'] = True
    client.publish(path, json.dumps(status))
    time.sleep(0.5)
    status['connected'] = False
    client.publish(path, json.dumps(status))
    time.sleep(0.5)
    """
