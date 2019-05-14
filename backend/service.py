import paho.mqtt.client as mqtt
import csv
import json
from time import time
import os
import sqlite3

class MissionControl(object):
    def __init__(self):
        self.buffer= []

        self.recording = False
        self.filename = None

        self.voltage = ['0.0']*144
        self.temperature = ['0.0']*144

        self.start = time()
        self.current = 0
        self.accumulator = 0    # Tími frá síðasta accumulator publish
        self.write = 0          # Tími frá síðustu csv uppfærslu

        self.gate = None
        self.laps = []
        self.gps_current = [0,0]
        self.gps_last = [0,0]
        self.energy = 0
        self.track = 0

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        client.subscribe("#")

    def on_message(self, client, userdata, msg):
        self.current = time() - self.start
        
        data = [self.current, msg.topic, msg.payload.decode("utf-8")]

        if data[1].split('/')[0] == 'spark':
            self.buffer.append(data)

        if self.current - self.write > 1:
            # Write to csv file if recording is on
            if self.recording:
                with open('data/' + self.filename, 'a') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(self.buffer)

                csv_file.close()

            status = {'recording': self.recording, 'total': 0, 'accumulator': 0, 'cooling': 0, 'datalogger': 0, 'dspace': 0, 'energy': 0, 'junctions': 0, 'track': self.track, 'x': self.gps_current[0], 'y': self.gps_current[1], 'laps': self.laps}

            for b in self.buffer:
                status[b[1].split('/')[1]] += 1

            status['total'] = len(self.buffer)
            print(status)

            client.publish('control/status', json.dumps(status))

            self.buffer.clear()
            self.write = self.current

        if msg.topic == 'spark/energy/total':
            self.energy = float(msg.payload.decode("utf-8"))

        if msg.topic == 'spark/datalogger/gps/longitudinal':
            self.gps_current[0] = float(msg.payload.decode("utf-8"))

        if msg.topic == 'spark/datalogger/gps/lateral':
            self.gps_current[1] = float(msg.payload.decode("utf-8"))

            try:
                if self.intersect(self.gps_current, self.gps_last, self.gate[0], self.gate[1]) and self.recording:
                    # Gate crossing detected
                    i = len(self.laps)
                    if i == 0:
                        self.laps.append({'id': i+1, 'time': round(self.current,2), 'energy': round(self.energy,2), 'dtime': 0, 'denergy': 0})
                    else:
                        time_delta = round(self.current - self.laps[i-1]['time'],2)
                        energy_delta = round(self.energy - self.laps[i-1]['energy'],2)
                        self.laps.append({'id': i+1, 'time': round(self.current,2), 'energy': round(self.energy,2), 'dtime': time_delta, 'denergy': energy_delta})
            
            except Exception as e:
                print(e)

            self.gps_last[0] = self.gps_current[0]
            self.gps_last[1] = self.gps_current[1]


        # Check if we have a request to start or stop recording
        if msg.topic == 'control/recording':
            cmd = json.loads(msg.payload.decode("utf-8"))
            print(cmd)

            if not self.recording and cmd['recording'] == 1:
                self.recording = True
                self.start = time()
                self.write = 0
                self.filename = cmd['filename']
                self.track = cmd['track']

                conn = sqlite3.connect('/home/brynjar/control_frontend/db.sqlite3')
                c = conn.cursor()
                c.execute("select points from control_track where id=%i" % (int(self.track)))
                
                try:
                    self.gate = json.loads(c.fetchone()[0])['gate']
                except Exception as e:
                    print("Could not load gate points")
                    self.gate = None

                print("Start recording")

            elif self.recording and cmd['recording'] == 0:
                self.recording = False
                size = os.path.getsize("/home/brynjar/control_backend/data/%s" % (self.filename))
                size = round(size/1024**2,2)
                duration = round(time()-self.start)

                conn = sqlite3.connect('/home/brynjar/control_frontend/db.sqlite3')
                c = conn.cursor()
                c.execute("update control_data set filesize=%f, duration=%i where id=(select max(id) from control_data);" % (size, duration))
                conn.commit()
                conn.close()

                self.track = 0
                self.laps = []
                print("Stop recording")
        
        # Parse and resend data to be used by frontend
        path = msg.topic.split('/')

        if path[2] == "temperature":
            self.temperature[int(path[3])-1] = msg.payload.decode("utf-8")

        if path[2] == "voltage":
            self.voltage[int(path[3])-1] = msg.payload.decode("utf-8")

        if self.current - self.accumulator > 3:
            client.publish('control/voltage', ' '.join(self.voltage))
            client.publish('control/temperature', ' '.join(self.temperature))
            
            self.accumulator = self.current

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
client.on_message = ctrl.on_message

client.username_pw_set('spark', 'spark')
client.connect("localhost", 1883, 60)

client.loop_forever()

