import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags,rc):
    print("connected with result code: "+str(rc))
    client.subscribe("dev/test")


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


count = 0
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883,60)
client.loop_start()

i = 0
while i < 10000:
    client.publish("ts/ams/voltage/2", count)
    count = count + 1
    i = i+1
    print(count)
    time.sleep(0.1)
