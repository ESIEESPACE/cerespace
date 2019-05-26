import datetime
import json
import sys
import threading
import time
import traceback
import cv2

import paho.mqtt.client as mqtt

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
                run_command(command)
        except Exception:
            print(msg.payload.decode("utf-8"))
            traceback.print_exc()


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


def command_to_gcode(command) -> str:
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


def run_command(command):
    if command[0] == "wait" and len(command) == 2:
        print("wait for {}ms".format(command[1]))
        time.sleep(command[1] / 1000)

    elif command[0] == "send":
        returned_message = ""
        for message in range(1, len(command) - 1):
            returned_message += command[message] + "\n"
        client.publish("farm/farm1/logs", returned_message)

    elif command[0] == "run":
        print("asked to run: " + command[1])

    elif command[0] == "photo":
        take_photo()

    else:
        try:
            print("returned G-CODE : {}".format(command_to_gcode(command)))
        except ValueError:
            traceback.print_exc()


def take_photo():
    print("Taking photo")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    img_name = "photos/opencv_frame_{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    cv2.imwrite(img_name, frame)
    cam.release()


def main_loop():
    while True:
        time.sleep(1)


if __name__ == '__main__':
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
