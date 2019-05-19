import json
import os
import time
import traceback
from os import listdir


def readinstant(data):
    gcode = ""
    for command in data["commands"]:
        runcommand(command)
    return


def readevent(data):
    return


def readsequence(data):
    printdebug("Sequence id: " + data["id"])
    printdebug("Sequence name: " + data["name"])

    for command in data["commands"]:
        runcommand(command)
    return


def runcommand(command):
    if command[0] == "wait" and len(command) == 2:
        printdebug("wait for {}ms".format(command[1]))
        time.sleep(command[1] / 1000)

    elif command[0] == "send":
        retmessage = ""
        for message in range(1, len(command) - 1):
            retmessage += command[message] + "\n"
        printdebug("send message : " + retmessage)

    elif command[0] == "run":
        printdebug("asked to run: " + command[1])

    else:
        try:
            printdebug("returned G-CODE : {}".format(commandtogcode(command)))
        except ValueError:
            traceback.print_exc()


def commandtogcode(command):
    if command[0] == "emergency":
        return "E"

    elif command[0] == "fakeapproved":
        return commandtogcode(["writeparam", 2, 1])

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
        raise ValueError("Invalid command")


def routejson(data):
    router = {
        "event": readevent,
        "sequence": readsequence,
        "instant": readinstant
    }
    try:
        router.get(data["type"])(data)
    except ValueError:
        traceback.print_exc()
        print("Invalid format")
    return


def printdebug(message):
    print("[DEBUG] " + message)


if __name__ == '__main__':
    fs = [f for f in listdir(os.path.dirname(os.path.realpath(__file__)) + "/../actions_exemple/")]
    for file in fs:
        printdebug("opening " + file)
        f = open(os.path.dirname(os.path.realpath(__file__)) + "/../actions_exemple/" + file, "r")
        filedata = f.read()
        try:
            routejson(json.loads(filedata))
        except ValueError:
            traceback.print_exc()
            print("invalid JSON file")
        f.close()
