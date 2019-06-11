import time
import serial
import traceback

from client import photos
from client import client

ser = serial.Serial()


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
        raise ValueError("Invalid command : " + str(command))


def run_command(command):
    print(str(command))
    if command[0] == "wait" and len(command) == 2:
        print("wait for {}ms".format(command[1]))
        time.sleep(command[1] / 1000)

    elif command[0] == "send":
        returned_message = ""
        for message in range(1, len(command) - 1):
            returned_message += command[message] + "\n"
        client.send_logs(returned_message)

    elif command[0] == "run":
        print("asked to run: " + command[1])

    elif command[0] == "setup":
        send_params()

    elif command[0] == "take_photo":
        photos.take_photo()

    else:
        try:
            print("returned G-CODE : {}".format(command_to_gcode(command)))
        except ValueError:
            traceback.print_exc()


def gcode_interpreter(command: str):
    try:
        command = command.decode('utf-8')
        command_dec = command.split(" ")
        command_type = 0

        data = {}

        for param in command_dec:
            # https://github.com/FarmBot/farmbot-arduino-firmware/#parameters-for-commands
            param = param.replace(' ', '')
            if param.startswith('R'):
                command_type = int(param.replace('R', ''))
            elif param.startswith('XA'):
                data[0] = param.replace('XA', '')
            elif param.startswith('XB'):
                data[1] = param.replace('XB', '')
            elif param.startswith('YA'):
                data[2] = param.replace('YA', '')
            elif param.startswith('YB'):
                data[3] = param.replace('YB', '')
            elif param.startswith('ZA'):
                data[4] = param.replace('ZA', '')
            elif param.startswith('ZB'):
                data[5] = param.replace('ZB', '')
            elif param.startswith('X'):
                data[0] = param.replace('X', '')
            elif param.startswith('Y'):
                data[1] = param.replace('Y', '')
            elif param.startswith('Z'):
                data[2] = param.replace('Z', '')
            elif param.startswith('P'):
                data[0] = param.replace('P', '')
            elif param.startswith('V'):
                data[1] = param.replace('V', '')

        if command_type == 0:
            print("Idle")
        elif command_type == 1:
            print("Command started")
        elif command_type == 2:
            print("Command succeed")
        elif command_type == 3:
            print("Command finished with error")
        elif command_type == 4:
            print("Command running")
        elif command_type == 5:
            print("Motor state : X=" + data[0] + " Y=" + data[1] + " Z=" + data[2])
            # https://github.com/FarmBot/farmbot-arduino-firmware/#axis-states-r05
        elif command_type == 6:
            print("Calibration state : X=" + data[0] + " Y=" + data[1] + " Z=" + data[2])
            # https://github.com/FarmBot/farmbot-arduino-firmware/#calibration-states-r06
        elif command_type == 7:
            print("Retry movement")
        elif command_type == 8:
            print("Echo : " + command)
        elif command_type == 9:
            print("Command invalid")
        elif command_type == 11:
            print("X axis homing complete")
        elif command_type == 12:
            print("Y axis homing complete")
        elif command_type == 13:
            print("Z axis homing complete")
        elif command_type == 21:
            print("Parameter : " + data[0] + " " + data[1])
        elif command_type == 31:
            print("Status : " + data[0] + " " + data[1])
        elif command_type == 41:
            print("Pin : " + data[0] + " " + data[1])
        elif command_type == 82:
            print("Motor coord : X=" + data[0] + " Y=" + data[1] + " Z=" + data[2])
        elif command_type == 81:
            print("End stops X:" + data[0] + " " + data[1] + " Y:" + data[2] + " " + data[3] + " Z:" + data[4] + " " +
                  data[5])
        elif command_type == 84 or command_type == 85:
            pass
        elif command_type == 88:
            print("No params")
            send_params()
        elif command_type == 99:
            print("DEBUG : " + command)
        else:
            print(command)
    except:
        traceback.print_exc()


def send_params():
    pass


def connect():
    global ser
    ser.baudrate = 115200
    ser.port = '/dev/ttyACM0'
    ser.open()
