import json
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
    if msg.topic == "farm/farm1/instants":
        try:
            commands = json.loads(msg.payload.decode("utf-8"))
            for command in commands:
                print(command_to_gcode(command))

        except Exception:
            print(msg.payload.decode("utf-8"))
            traceback.print_exc()


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


def command_to_gcode(command):
    if command[0] == "emergency":
        return "E"

    elif command[0] == "fakeapproved":
        return command_to_gcode(["writeparam", 2, 1])

    elif command[0] == "go" and len(command) == 2:
        return "G00 X{} Y{} Z{}".format(command[1][0], command[1][1], command[1][2])

    elif command[0] == "home" and len(command) == 2:
        if command[1] == "X":
            return "F11"
        elif command[1] == "Y":
            return "F12"
        elif command[1] == "Z":
            return "F13"

    elif command[0] == "read" and len(command) == 3:
        return "F42 P{} M{}".format(command[1], command[2])

    elif command[0] == "write" and len(command) == 3:
        return "F32 P{} V{}".format(command[1], command[2])

    elif command[0] == "write" and len(command) == 6:
        return "F32 P{} V{} W{} T{} M{}".format(command[1], command[2], command[3], command[4], command[5])

    elif command[0] == "writeparam" and len(command) == 3:
        return "F22 P{} V{}".format(command[1], command[2])

    elif command[0] == "getparam" and len(command) == 2:
        return "F21 P{}".format(command[1])

    elif command[0] == "getpos" and len(command) == 1:
        return "F82"

    else:
        raise ValueError("Invalid command : " + command)


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
