import json
import sys
import threading
import time
import traceback

import paho.mqtt.client as mqtt

from client import run

client = mqtt.Client()


def on_connect(client: mqtt.Client, userdata, flags, rc: int):
    print("Connected with result code " + str(rc))
    client.subscribe("farm/farm1")
    client.subscribe("farm/farm1/instants")


def on_disconnect(client, userdata, rc: int):
    print("Disconnected with result code " + str(rc))


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    if msg.topic == "farm/farm1/instants":
        try:
            commands = json.loads(msg.payload.decode("utf-8"))
            for command in commands:
                run.run_command(command)
        except Exception:
            print(msg.payload.decode("utf-8"))
            traceback.print_exc()


def send_logs(message):
    client.publish("/farm/farm1/logs", message)


def connect():
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    if len(sys.argv) > 1:
        client.connect(sys.argv[1], 1883, 60)
    else:
        client.connect("mqtt", 1883, 60)


def ping(slp: int = 60):
    print("Starting ping service\n")
    while True:
        try:
            client.publish("farm/farm1", '["ping"]')
        except:
            pass

        time.sleep(slp)


def main_loop():
    while True:
        time.sleep(1)


def main():
    print("Starting CERESPACE Client")
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


if __name__ == '__main__':
    main()
