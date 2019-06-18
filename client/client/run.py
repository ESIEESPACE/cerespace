import os
import time
import serial
import traceback
import json
import sqlite3

from datetime import datetime

from client import photos
from client import client

ser = serial.Serial()

queue = 0

emergency_state = False

parameters_change = False
parameters = {
    3: "0",  # PARAM_USE_EEPROM
    4: "1",  # PARAM_E_STOP_ON_MOV_ERR
    5: "1",  # PARAM_MOV_NR_RETRY
    11: "120",  # MOVEMENT_TIMEOUT_X
    12: "120",  # MOVEMENT_TIMEOUT_Y
    13: "120",  # MOVEMENT_TIMEOUT_Z
    15: "0",  # MOVEMENT_KEEP_ACTIVE_X
    16: "0",  # MOVEMENT_KEEP_ACTIVE_Y
    17: "0",  # MOVEMENT_KEEP_ACTIVE_Z
    18: "1",  # MOVEMENT_HOME_AT_BOOT_X
    19: "1",  # MOVEMENT_HOME_AT_BOOT_Y
    20: "1",  # MOVEMENT_HOME_AT_BOOT_Z
    21: "0",  # MOVEMENT_INVERT_ENDPOINTS_X
    22: "0",  # MOVEMENT_INVERT_ENDPOINTS_Y
    23: "0",  # MOVEMENT_INVERT_ENDPOINTS_Z
    25: "1",  # MOVEMENT_ENABLE_ENDPOINTS_X
    26: "1",  # MOVEMENT_ENABLE_ENDPOINTS_Y
    27: "1",  # MOVEMENT_ENABLE_ENDPOINTS_Z
    31: "1",  # MOVEMENT_INVERT_MOTOR_X
    32: "1",  # MOVEMENT_INVERT_MOTOR_Y
    33: "0",  # MOVEMENT_INVERT_MOTOR_Z
    36: "1",  # MOVEMENT_SECONDARY_MOTOR_X
    37: "1",  # MOVEMENT_SECONDARY_MOTOR_INVERT_X
    41: "",  # MOVEMENT_STEPS_ACC_DEC_X
    42: "",  # MOVEMENT_STEPS_ACC_DEC_Y
    43: "",  # MOVEMENT_STEPS_ACC_DEC_Z
    45: "1",  # MOVEMENT_STOP_AT_HOME_X
    46: "1",  # MOVEMENT_STOP_AT_HOME_Y
    47: "0",  # MOVEMENT_STOP_AT_HOME_Z
    51: "",  # MOVEMENT_HOME_UP_X
    52: "",  # MOVEMENT_HOME_UP_Y
    53: "",  # MOVEMENT_HOME_UP_Z
    55: "5",  # MOVEMENT_STEP_PER_MM_X
    56: "5",  # MOVEMENT_STEP_PER_MM_Y
    57: "25",  # MOVEMENT_STEP_PER_MM_Z
    61: "50",  # MOVEMENT_MIN_SPD_X
    62: "50",  # MOVEMENT_MIN_SPD_Y
    63: "50",  # MOVEMENT_MIN_SPD_Z
    65: "100",  # MOVEMENT_HOME_SPD_X
    66: "80",  # MOVEMENT_HOME_SPD_Y
    67: "80",  # MOVEMENT_HOME_SPD_Z
    71: "150",  # MOVEMENT_MAX_SPD_X
    72: "80",  # MOVEMENT_MAX_SPD_Y
    73: "100",  # MOVEMENT_MAX_SPD_Z
    75: "",  # MOVEMENT_INVERT_2_ENDPOINTS_X
    76: "",  # MOVEMENT_INVERT_2_ENDPOINTS_Y
    77: "",  # MOVEMENT_INVERT_2_ENDPOINTS_Z
    101: "0",  # ENCODER_ENABLED_X
    102: "0",  # ENCODER_ENABLED_Y
    103: "0",  # ENCODER_ENABLED_Z
    105: "",  # ENCODER_TYPE_X
    106: "",  # ENCODER_TYPE_Y
    107: "",  # ENCODER_TYPE_Z
    111: "",  # ENCODER_MISSED_STEPS_MAX_X
    112: "",  # ENCODER_MISSED_STEPS_MAX_Y
    113: "",  # ENCODER_MISSED_STEPS_MAX_Z
    115: "",  # ENCODER_SCALING_X
    116: "",  # ENCODER_SCALING_Y
    117: "",  # ENCODER_SCALING_Z
    121: "",  # ENCODER_MISSED_STEPS_DECAY_X
    122: "",  # ENCODER_MISSED_STEPS_DECAY_Y
    123: "",  # ENCODER_MISSED_STEPS_DECAY_Z
    125: "",  # ENCODER_USE_FOR_POS_X
    126: "",  # ENCODER_USE_FOR_POS_Y
    127: "",  # ENCODER_USE_FOR_POS_Z
    131: "",  # ENCODER_INVERT_X
    132: "",  # ENCODER_INVERT_Y
    133: "",  # ENCODER_INVERT_Z
    141: "",  # MOVEMENT_AXIS_NR_STEPS_X
    142: "",  # MOVEMENT_AXIS_NR_STEPS_Y
    143: "",  # MOVEMENT_AXIS_NR_STEPS_Z
    145: "1",  # MOVEMENT_STOP_AT_MAX_X
    146: "1",  # MOVEMENT_STOP_AT_MAX_Y
    147: "1",  # MOVEMENT_STOP_AT_MAX_Z
    201: "",  # PIN_GUARD_1_PIN_NR
    202: "",  # PIN_GUARD_1_TIME_OUT
    203: "",  # PIN_GUARD_1_ACTIVE_STATE
    205: "",  # PIN_GUARD_2_PIN_NR
    206: "",  # PIN_GUARD_2_TIME_OUT
    207: "",  # PIN_GUARD_2_ACTIVE_STATE
}

pompe = 10


def command_to_gcode(command) -> str:
    global parameters_change
    global emergency_state

    if command[0] == "emergency":
        emergency_state = True
        client.mqtt_client.publish("farm/farm1/emergency", 0)
        return "E"

    elif command[0] == "fakeapproved":
        return command_to_gcode(["writeparam", 2, 1])

    elif command[0] == "go" and len(command) == 2:
        if int(command[1][2]) > 0:
            command[1][2] = 0
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
        parameters_change = True
        parameters[int(command[1])] = command[2]
        return "F22 P{} V{}".format(command[1], command[2])

    elif command[0] == "getparam" and len(command) == 2:
        return "F21 P{}".format(command[1])

    elif command[0] == "getpos" and len(command) == 1:
        return "F82"

    elif command[0] == "reset_emergency" and len(command) == 1:
        client.mqtt_client.publish("farm/farm1/emergency", 0)
        emergency_state = False
        return "F09"

    elif command[0] == "report_params" and len(command) == 1:
        return "F20"

    elif command[0] == "water" and len(command) == 1:
        return "F44 P{} V1 W0 T10000 M0".format(pompe)

    else:
        raise ValueError("Invalid command : " + str(command))


def run_command(command):
    global queue
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
    elif command[0] == "send_params":
        send_params()
    else:
        try:
            print("returned G-CODE : {} Q{}".format(command_to_gcode(command), queue))
            queue += 1
            ser.write((command_to_gcode(command) + "\r\n").encode())
        except ValueError:
            traceback.print_exc()


def gcode_interpreter(command: str):
    global queue
    global emergency_state
    if queue > 0:
        queue = 0
    try:
        command = command.decode('utf-8')
        command_dec = command.split(" ")
        command_type = 0

        data = {
            "X": "",
            "Y": "",
            "Z": "",
            "P": "",
            "Q": "",
        }

        for param in command_dec:
            # https://github.com/FarmBot/farmbot-arduino-firmware/#parameters-for-commands
            param = param.replace(' ', '')
            if param.startswith('R'):
                try:
                    command_type = int(param.replace('R', ''))
                except:
                    traceback.print_exc()
                    print(param)
            elif param.startswith('XA'):
                data["XA"] = param.replace('XA', '')
            elif param.startswith('XB'):
                data["XB"] = param.replace('XB', '')
            elif param.startswith('YA'):
                data["YA"] = param.replace('YA', '')
            elif param.startswith('YB'):
                data["YB"] = param.replace('YB', '')
            elif param.startswith('ZA'):
                data["ZA"] = param.replace('ZA', '')
            elif param.startswith('ZB'):
                data["ZB"] = param.replace('ZB', '')
            elif param.startswith('X'):
                data["X"] = param.replace('X', '')
            elif param.startswith('Y'):
                data["Y"] = param.replace('Y', '')
            elif param.startswith('Z'):
                data["Z"] = param.replace('Z', '')
            elif param.startswith('P'):
                data["P"] = param.replace('P', '')
            elif param.startswith('V'):
                data["V"] = param.replace('V', '')
            elif param.startswith("Q"):
                data["Q"] = param.replace('Q', '')

        if command_type == 0:
            print("Idle")
        elif command_type == 1:
            print("Command started")
        elif command_type == 2:
            print("Command succeed")
            queue -= 1
        elif command_type == 3:
            print("Command finished with error")
            queue -= 1
        elif command_type == 4:
            print("Command running")
        elif command_type == 5:
            try:
                print("Motor state : X=" + get_motor_state(data["X"]) + " Y=" + get_motor_state(
                    data["Y"]) + " Z=" + get_motor_state(data["Z"]))
            except KeyError:
                traceback.print_exc()
                print(command)
            # https://github.com/FarmBot/farmbot-arduino-firmware/#axis-states-r05
        elif command_type == 6:
            print("Calibration state : X=" + data["X"] + " Y=" + data["Y"] + " Z=" + data["Z"])
            # https://github.com/FarmBot/farmbot-arduino-firmware/#calibration-states-r06
        elif command_type == 7:
            print("Retry movement")
        elif command_type == 8:
            print("Echo : " + command)
        elif command_type == 9:
            print("Command invalid")
            queue -= 1
        elif command_type == 11:
            print("X axis homing complete")
        elif command_type == 12:
            print("Y axis homing complete")
        elif command_type == 13:
            print("Z axis homing complete")
        elif command_type == 21:
            print("Parameter : " + data["P"] + " " + data["V"])
            client.mqtt_client.publish("farm/farm1/params", "{\"P\":" + data["P"] + ", \"V\":" + data["V"] + "}")
        elif command_type == 31:
            print("Status : " + data["P"] + " " + data["V"])
        elif command_type == 41:
            print("Pin : " + data["P"] + " " + data["V"])
        elif command_type == 82:
            print("Motor coord : X=" + data["X"] + " Y=" + data["Y"] + " Z=" + data["Z"])
            client.mqtt_client.publish("farm/farm1/position",
                                       "{\"X\": " + data["X"] + ", \"Y\": " + data["Y"] + ", \"Z\": " + data["Z"] + "}")
        elif command_type == 81:
            print("End stops X:" + data["XA"] + " " + data["XB"] + " Y:" + data["YA"] + " " + data["YB"] + " Z:" + data[
                "ZA"] + " " +
                  data["ZB"])
        elif command_type == 84 or command_type == 85:
            pass
        elif command_type == 87:
            client.mqtt_client.publish("farm/farm1/emergency", 1)
            emergency_state = True
            print("Emergency return")
        elif command_type == 88:
            print("No params")
            send_params()
        elif command_type == 99:
            print("DEBUG : " + command)
        else:
            print(command)
    except:
        traceback.print_exc()
    if queue > 0:
        queue = 0


def send_params():
    client.db_curs.execute('''SELECT * FROM settings''')
    data = client.db_curs.fetchall()
    for param in data:
        try:

            if param[1] != "":
                send_important_command("F22 P{} V{}".format(param[0], param[1]))
                print("Send command: " + str(param[0]))
        except KeyError:
            ""
        except:
            traceback.print_exc()
    send_important_command("F22 P2 V1")
    send_important_command("F43 P{} V1".format(pompe))
    send_important_command("F41 P{} V0 M0".format(pompe))
    print("Send params")
    home()


def home():
    send_important_command("F11", 10000)

    send_important_command("F12", 10000)

    send_important_command("F13", 10000)


def connect():
    global ser
    ser.baudrate = 115200
    ser.port = '/dev/ttyACM0'
    ser.open()


def get_motor_state(val) -> str:
    if val == "":
        return ""
    val = int(val)
    if val == 0:
        return "Idle"
    elif val == 1:
        return "Starting motor"
    elif val == 2:
        return "Accelerating"
    elif val == 3:
        return "Cruising"
    elif val == 4:
        return "Decelerating"
    elif val == 5:
        return "Stopping motor"
    elif val == 6:
        return "Crawling"
    else:
        return "Unknown state"


def send_important_command(command: str, timeout: int = 10000):
    while command_sync(command, timeout=timeout) is False:
        print("Command " + command + " failed, retry")


def command_sync(command: str, timeout: int = 1000) -> bool:
    stime = datetime.now().timestamp()
    ser.write((command + "\r\n").encode())
    rdline = ""
    while True:
        rdline = ser.readline()
        lrdline = str(rdline)
        if emergency_state:
            ser.write("F09\r\n".encode())
        elif "R02" in lrdline:
            return True
        elif "R03" in lrdline:
            return False
        elif stime + timeout < datetime.now().timestamp() and timeout != -1:
            return False
        else:
            gcode_interpreter(rdline)
    return False
