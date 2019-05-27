import time
import traceback

from client import photos
from client import client


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
        client.send_logs(returned_message)

    elif command[0] == "run":
        print("asked to run: " + command[1])

    elif command[0] == "photo":
        photos.take_photo()

    else:
        try:
            print("returned G-CODE : {}".format(command_to_gcode(command)))
        except ValueError:
            traceback.print_exc()
