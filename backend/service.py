import paho.mqtt.client as mqtt
import asyncio
import time
import os
import json
from gps import gps
import sqlite3

class MissionControl(object):
    def __init__(self):
        """
        This function initializes the object.

        Two variables are initialized, a buffer for incoming data, and a
        variable for the timestamp of last update sent to clients.
        """
        self.buffer= []
        self.send_time = 0
        self.client_id = 'ts'

        self.time_received = 0  # Time of last client msg reseaved
        self.client_timeout = 1 # Time until client connection status timeout

    def on_connect(self, client, userdata, flags, rc):
        """
        This function is triggered when an MQTT connection is established.
        """
        print("Connected with result code "+str(rc))

        client.subscribe(self.client_id+"/#")

    def is_client_connected(self):
        """
        This function monitor that the client is connected by observing
        if packets are reseaved from client.
        """

        if time.time()-self.time_received < self.client_timeout:
            return True
        else:
            return False

    def on_message(self, client, userdata, msg):
        """
        This function is triggered every time an MQTT message is received.

        All received messages are collected into the self.buffer list. When
        a message arrives and the self.send_time timestamp is over a second
        in the past, two MQTT messages are published.

        "control/latest" is sent a JSON dictionary with one (latest) value
        from each received topic in the last second.

        "control/count" is sent a JSON dictionary with the number of
        messages received from each topic in the last second.
        """

        # Structure the message and add to the buffer
        data = [msg.topic, msg.payload.decode("utf-8")]

        if data[0].split('/')[0] == self.client_id:
            self.buffer.append(data)
            #print(msg.topic)
            self.time_received = time.time()



        if GPS.gps_gather(data) and self.is_client_connected():
            GPS.calc_distance()
            GPS.calc_lap_time()
            GPS.publish(client)


        # Code that is executed every second
        if time.time() - self.send_time > 1:

            values_latest = {}
            values_count = {}


            for b in self.buffer:

                # Add msg to latest buffer that will be transited to front end
                values_latest[b[0]] = b[1]

                # Count the topic samling rate. Count = 1 if not counted yet
                if b[0] in values_count:
                    values_count[b[0]] += 1
                else:
                    values_count[b[0]] = 1

            client.publish('control/latest', json.dumps(values_latest))
            client.publish('control/count', json.dumps(values_count))


            # Clear buffer and reset timer
            self.buffer.clear()
            self.send_time = time.time()


if __name__ == "__main__":
    ctrl = MissionControl()

    client = mqtt.Client()
    client.on_connect = ctrl.on_connect
    client.on_message = ctrl.on_message

    #client.username_pw_set('spark', 'spark')
    client.connect("localhost", 1883, 60)

    client.loop_start()

    GPS = gps()

    start_time = time.time()
    start = True
    sqlite_path = "D:\dev\mission-control-github\db.sqlite3"
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()

    while True:
        status = {
            'connected': ctrl.is_client_connected()
        }
        # Run every second
        if time.time()-start_time >1:
            start_time = time.time()
            client.publish('control/status', json.dumps(status))

        #Sets start time on connect
        if  status['connected'] == start:
            start = not start
            if status['connected']:

                c.execute("select points from control_track where id=%i" % (int(5)))
                try:
                    gate = json.loads(c.fetchone()[0])['gate']
                except Exception as e:
                    print("Could not load gate points")
                    gate = None
                GPS.set_start(time.time(), gate)
        # Get gate point on connet
        time.sleep(0.01)
