import paho.mqtt.client as mqtt
import csv
import json
import os
import sqlite3
from time import time
from subprocess import check_call
from math import sin, cos, sqrt, atan2, radians

class MissionControl(object):
    # Initialize variables
    def __init__(self):
        self.buffer= []                 # Data is collected to the buffer, then written to file and buffer emptied

        self.recording = False          # Is recording mode enabled or not, i.e. should be writing to a file
        self.filename = None            # Name of the csv file to write to, if recording mode is enabled

        self.voltage = ['0.0']*144      # Buffer for voltage values published every second to MQTT
        self.temperature = ['0.0']*144  # Buffer for temperature values published every second to MQTT
        self.distance = 0               # Distance of current recording in kilometers, is incremented when GPS is received

        self.start = 0                  # Timestamp when recording was started
        self.current = 0                # Timestamp of current message
        self.accumulator = 0            # Tími frá síðasta accumulator publish
        self.write = 0                  # Timestamp of last file write

        # Lap time calculation variables

        self.gate = None                # Two GPS points that define a starting gate, if None lap times won't be calculated
        self.laps = []                  # Values for each lap are stored as a dictionary in this list
        self.gps_current = [0,0]        # Latest received GPS coordinate, used to check if path intersects starting gate
        self.gps_last = [0,0]           # Second latest received GPS coordinate
        self.energy = 0                 # Latest received energy value from the energy meter
        self.track = 0                  # Primary key of track in sqlite database

        self.sqlite_path = "/home/spark/mission-control/db.sqlite3"
        self.csv_path = "/home/spark/mission-control/data/"

    # Function that is used as a hook for the MQTT client when connection is successful
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        client.subscribe("#")

    def beta_message(self, client, userdata, msg):
        try:
            self.on_message(client, userdata, msg)
        except Exception as e:
            print(e)
            exit()

    # Function that is used as a hook for the MQTT client when a message is received
    def on_message(self, client, userdata, msg):
        if (msg.topic[0:5] != "spark" and msg.topic[0:7] != "control") or msg.topic.count('/') < 1:
            return

        print(msg.topic)

        # Set timestamp of current message
        self.current = time() - self.start
        
        # Structure the message and add to buffer if it belongs to a car telemetry path
        data = [self.current, msg.topic, msg.payload.decode("utf-8")]

        if data[1].split('/')[0] == 'spark':
            self.buffer.append(data)

        # Code that is executed every second
        if self.current - self.write > 1:

            # Write buffer to csv file if recording is enabled
            if self.recording:
                with open(self.csv_path + self.filename, 'a') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(self.buffer)

                csv_file.close()

            # Count messages in the buffer by which subsystem they belong to
            status = {
                'recording': self.recording, 
                'total': 0, 
                'accumulator': 0, 
                'cooling': 0, 
                'datalogger': 0, 
                'dspace': 0, 
                'energy': 0, 
                'junctions': 0, 
                'track': self.track, 
                'x': self.gps_current[0], 
                'y': self.gps_current[1], 
                'laps': self.laps
            }

            values_latest = {}
            values_count = {}

            for b in self.buffer:
                if b[1].split('/')[1] in status:
                    status[b[1].split('/')[1]] += 1

                values_latest[b[1]] = b[2]

                if b[1] in values_count:
                    values_count[b[1]] += 1
                else:
                    values_count[b[1]] = 1

            status['total'] = len(self.buffer)

            client.publish('control/latest', json.dumps(values_latest))
            client.publish('control/count', json.dumps(values_count))
            client.publish('control/status', json.dumps(status))
            client.publish('control/voltage', ' '.join(self.voltage))
            client.publish('control/temperature', ' '.join(self.temperature))

            print(self.distance)

            # Clear buffer and reset timer
            self.buffer.clear()
            self.write = self.current

        # Collect GPS coordinates and energy meter value to calculate lap times
        if msg.topic == 'spark/energy/total':
            self.energy = float(msg.payload.decode("utf-8"))

        if msg.topic == 'spark/datalogger/gps/longitudinal':
            self.gps_current[0] = float(msg.payload.decode("utf-8"))

        if msg.topic == 'spark/datalogger/gps/lateral':
            self.gps_current[1] = float(msg.payload.decode("utf-8"))

            if self.gps_last[0] != 0:
                dlon = radians(self.gps_current[0]) - radians(self.gps_last[0])
                dlat = radians(self.gps_current[1]) - radians(self.gps_last[1])

                a = sin(dlat / 2)**2 + cos(self.gps_last[1]) * cos(self.gps_current[1]) * sin(dlon / 2)**2
                self.distance += 2 * 6373 * atan2(sqrt(a), sqrt(1 - a))

            # Check if GPS path intersects the starting line
            if self.gate is not None:
                if self.intersect(self.gps_current, self.gps_last, self.gate[0], self.gate[1]) and self.recording:
                    
                    # Get the lap number and append the latest lap
                    i = len(self.laps)
                    
                    if i == 0:
                        self.laps.append({
                            'id': i+1, 
                            'time': round(self.current,2), 
                            'energy': round(self.energy,2), 
                            'dtime': 0, 
                            'denergy': 0
                        })
                    
                    else:
                        time_delta = round(self.current - self.laps[i-1]['time'],2)
                        energy_delta = round(self.energy - self.laps[i-1]['energy'],2)
                        
                        self.laps.append({
                            'id': i+1, 
                            'time': round(self.current,2), 
                            'energy': round(self.energy,2), 
                            'dtime': time_delta, 
                            'denergy': energy_delta
                        })

            self.gps_last[0] = self.gps_current[0]
            self.gps_last[1] = self.gps_current[1]

        # Check if we have a request to start or stop recording
        if msg.topic == 'control/recording':
            cmd = json.loads(msg.payload.decode("utf-8"))
            self.recording_mode(cmd)

        # Add temperature and voltage values to a list that is published every second
        path = msg.topic.split('/')

        if path[1] == 'accumulator':
            if path[2] == "temperature":
                self.temperature[int(path[3])-1] = msg.payload.decode("utf-8")

            elif path[2] == "voltage":
                self.voltage[int(path[3])-1] = msg.payload.decode("utf-8")

    # Enables or disables recording mode according to JSON command
    def recording_mode(self, cmd):
        conn = sqlite3.connect(self.sqlite_path)
        c = conn.cursor()
        
        if not self.recording and cmd['recording'] == 1:
            self.recording = True
            self.start = time()
            self.write = 0
            self.distance = 0
            self.filename = cmd['filename']
            self.track = cmd['track']
            self.buffer.clear()

            c.execute("select points from control_track where id=%i" % (int(self.track)))
            
            try:
                self.gate = json.loads(c.fetchone()[0])['gate']
            except Exception as e:
                print("Could not load gate points")
                self.gate = None

        elif self.recording and cmd['recording'] == 0:
            self.recording = False

            # Compress the csv file
            check_call(['gzip', self.csv_path + self.filename])

            size = os.path.getsize(self.csv_path + self.filename + '.gz')
            duration = round(time()-self.start)

            c.execute("update control_data set filesize=%f, filename='%s', duration=%i, distance=%f where id=(select max(id) from control_data);" % (size, self.filename + '.gz', duration, self.distance))

            self.gate = None
            self.track = 0
            self.distance = 0
            self.laps = []
    
        conn.commit()
        conn.close()

    # Takes in endpoints of two lines as lists [x,y] and checks if the lines intersect or not
    def intersect(self, a1, a2, b1, b2):
        def f(x,y):
            return (x-a1[0])*(a2[1]-a1[1])-(y-a1[1])*(a2[0]-a1[0])

        def g(x,y):
            return (x-b1[0])*(b2[1]-b1[1])-(y-b1[1])*(b2[0]-b1[0])

        u = f(b1[0], b1[1])*f(b2[0], b2[1])
        v = g(a1[0], a1[1])*g(a2[0], a2[1])

        return (u < 0 and v < 0)

ctrl = MissionControl()

client = mqtt.Client()
client.on_connect = ctrl.on_connect
client.on_message = ctrl.beta_message

client.username_pw_set('spark', 'spark')
client.connect("localhost", 1883, 60)

client.loop_forever()

