import paho.mqtt.client as mqtt

from time import time
import os
import json

class MissionControl(object):
    def __init__(self):
        self.buffer= []                 # Data is collected to the buffer and emptied once per second

        self.current = 0                # Timestamp of current message
        self.write = 0                  # Timestamp of last file write

    def on_connect(self, client, userdata, flags, rc):
        """
        This function is triggered when an MQTT connection is established.
        """
        print("Connected with result code "+str(rc))

        client.subscribe("ts/#")

    def on_message(self, client, userdata, msg):
        """
        This function is triggered every time an MQTT message is received.
        """
        print(msg.topic)

        self.current = time() - self.start
        
        # Structure the message and add to the buffer
        data = [self.current, msg.topic, msg.payload.decode("utf-8")]

        self.buffer.append(data)

        # Code that is executed every second
        if self.current - self.write > 1:

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

            # Clear buffer and reset timer
            self.buffer.clear()
            self.write = self.current

ctrl = MissionControl()

client = mqtt.Client()
client.on_connect = ctrl.on_connect
client.on_message = ctrl.beta_message

# The MQTT connection details should be read from ENV variables
client.username_pw_set('spark', 'spark')
client.connect("localhost", 1883, 60)

client.loop_forever()

