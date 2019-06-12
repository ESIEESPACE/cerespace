import time
import serial
import traceback

from client import photos
from client import client

ser = serial.Serial()

parameters = {
    2: "1",  # PARAM_CONFIG_OK
    3: "0",  # PARAM_USE_EEPROM
    4: "0",  # PARAM_E_STOP_ON_MOV_ERR
    5: "3",  # PARAM_MOV_NR_RETRY
    11: "120",  # MOVEMENT_TIMEOUT_X
    12: "120",  # MOVEMENT_TIMEOUT_Y
    13: "120",  # MOVEMENT_TIMEOUT_Z
    15: "0",  # MOVEMENT_KEEP_ACTIVE_X
    16: "0",  # MOVEMENT_KEEP_ACTIVE_Y
    17: "0",  # MOVEMENT_KEEP_ACTIVE_Z
    18: "0",  # MOVEMENT_HOME_AT_BOOT_X
    19: "0",  # MOVEMENT_HOME_AT_BOOT_Y
    20: "0",  # MOVEMENT_HOME_AT_BOOT_Z
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
    47: "1",  # MOVEMENT_STOP_AT_HOME_Z
    51: "",  # MOVEMENT_HOME_UP_X
    52: "",  # MOVEMENT_HOME_UP_Y
    53: "",  # MOVEMENT_HOME_UP_Z
    55: "5",  # MOVEMENT_STEP_PER_MM_X
    56: "5",  # MOVEMENT_STEP_PER_MM_Y
    57: "25",  # MOVEMENT_STEP_PER_MM_Z
    61: "50",  # MOVEMENT_MIN_SPD_X
    62: "50",  # MOVEMENT_MIN_SPD_Y
    63: "2",  # MOVEMENT_MIN_SPD_Z
    65: "100",  # MOVEMENT_HOME_SPD_X
    66: "80",  # MOVEMENT_HOME_SPD_Y
    67: "20",  # MOVEMENT_HOME_SPD_Z
    71: "150",  # MOVEMENT_MAX_SPD_X
    72: "80",  # MOVEMENT_MAX_SPD_Y
    73: "16",  # MOVEMENT_MAX_SPD_Z
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
    elif command[0] == "reset_emergency" and len(command) == 1:
        return "F09"

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
    elif command[0] == "send_params":
        send_params()

    else:
        try:
            print("returned G-CODE : {}".format(command_to_gcode(command)))
            ser.write((command_to_gcode(command) + "\r\n").encode())
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
                try:
                    command_type = int(param.replace('R', ''))
                except:
                    traceback.print_exc()
                    print(param)
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
    for param_id in range(3, 224):
        try:
            if parameters[param_id] != "":
                ser.write("F22 P{} V{} \r\n".format(param_id, parameters[param_id]).encode())
                time.sleep(0.1)
                print("Send command: " + str(param_id))
        except KeyError:
            ""
        except:
            traceback.print_exc()
    ser.write("F22 P2 V1\r\n".encode())
    print("Send params")


def connect():
    global ser
    ser.baudrate = 115200
    ser.port = '/dev/ttyACM0'
    ser.open()
