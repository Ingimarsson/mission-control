import paho.mqtt.client as mqtt

from time import time
import os
import json

class MissionControl(object):
    def __init__(self):
        """
        This function initializes the object.

        Two variables are initialized, a buffer for incoming data, and a
        variable for the timestamp of last update sent to clients.
        """
        self.buffer= []
        self.send_time = 0

    def on_connect(self, client, userdata, flags, rc):
        """
        This function is triggered when an MQTT connection is established.
        """
        print("Connected with result code "+str(rc))

        client.subscribe("ts/#")

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
        print(msg.topic)

        # Structure the message and add to the buffer
        data = [msg.topic, msg.payload.decode("utf-8")]

        self.buffer.append(data)

        # Code that is executed every second
        if time() - self.send_time > 1:

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
            self.send_time = time()


if __name__ == "__main__":
    ctrl = MissionControl()

    client = mqtt.Client()
    client.on_connect = ctrl.on_connect
    client.on_message = ctrl.on_message

    #client.username_pw_set('spark', 'spark')
    client.connect("localhost", 1883, 60)

    client.loop_forever()
