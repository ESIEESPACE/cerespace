import sys
import threading
import time
import traceback

import paho.mqtt.client as mqtt

client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("farm/farm1")
    client.subscribe("farm/farm1/instants")


def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))


def on_message(client, userdata, msg):
    if msg.topic is "instant":
        print("Instant : " + str(msg.payload))
    # print(msg.topic + " " + str(msg.payload))


def connect():
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect("mqtt", 1883, 60)


def ping(slp=60):
    while True:
        try:
            client.publish("farm/farm1", '["ping"]')
        except:
            pass

        time.sleep(slp)


def main_loop():
    while True:
        pass


if __name__ == '__main__':
    connect()
    client.loop_start()

    ping_process = threading.Thread(target=ping)
    ping_process.setDaemon(True)
    ping_process.start()

    try:
        main_loop()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)

    client.loop_stop()
    sys.exit(0)
