from serial import Serial, SerialException
from time import sleep
from json import loads, JSONDecodeError

from luxmeters.serial_utils import list_ports, find_all_luxmeters


# from vendor.luxmeters.konica.CL200A import CL200A


def _read_response(resp, obj):
    try:
        resp = resp.splitlines()
        if len(resp):
            # print("We got multiple lines of output!")
            # print(f"'{resp}'")
            out = loads(resp[-1].split(' = ')[1])
        else:
            out = None
    except IndexError:
        try:
            print("Getting resp failed, retrying...")
            new_read = obj.read().splitlines()
            if len(new_read):
                print("We got multiple lines of output!")
                print(f"'{new_read}'")
                out = loads(new_read[-1].split(' = ')[1])
            else:
                out = None
        except IndexError:
            raise Exception(f"Got: {resp}")
    except JSONDecodeError:
        print("JSONDecodeError!")
        raise Exception(f"Got: {resp}")
    return out


def read_response(obj):
    obj.conn.flush()
    sleep(.1)
    return _read_response(obj.read(), obj)


class NeoLightsCtl:
    def __init__(self):
        try_to_find_serial = find_all_luxmeters('CH340', 'description')
        if try_to_find_serial:
            device = try_to_find_serial[0]
            print(f"Found device at: {device}")
        else:
            raise ValueError("Could not find the serial port of lights...")

        baud = 115200
        try:
            self.conn = Serial(device, baud)
        except SerialException:
            raise ValueError("Could not connect to serial device")

        print("Waiting 1 sec while initializing...")
        sleep(1)

        # self.set_brightness(20)

        self.pixels_count = self.get_pixels_count()

        resp_data = self.get_colors()
        try:
            self.power = bool(1 if resp_data['POWER'] == "ON" else 0)
            self.color = resp_data['Color']

            hsb = resp_data['HSBColor'].split(",")
            self.hue = int(hsb[0])
            self.saturation = int(hsb[1])
            self.brightness = int(hsb[2])

            self.channels = resp_data['Channel']
        except KeyError as err:
            print(f"Error at key {err}")
            print(f"resp_data: {resp_data}")
            exit(1)
        except IndexError:
            print(f"hsb IndexError! Data: {hsb}")
            exit(1)

        # Turn Off Wifi
        self.send_cmd("Wifi 0")

    def read(self):
        return self.conn.read(self.conn.in_waiting).decode('ascii')

    def send_cmd(self, cmd: str):
        self.conn.write(f"{cmd}\n".encode())

    def send_cmds(self, *cmd_list):
        # When sending multiple commands at once, you might get multiple lines of response
        cmd_str = "Backlog "
        for cmd in cmd_list:
            cmd_str += f"{cmd} ;"

        print("Executing multiple commands:")
        print(cmd_str)

        self.send_cmd(cmd_str)

    def get_pixels_count(self) -> int:
        self.send_cmd("Pixels")
        # sleep(2)
        return int(read_response(self)['Pixels'])

    def get_colors(self) -> dict:
        self.send_cmd("HSBColor")
        return read_response(self)

    def set_led(self, led_num: int, color):
        self.send_cmd(f"Led{led_num} {color}")

    def set_brightness(self, brightness: int):
        if not isinstance(brightness, int) or brightness < 0 or brightness > 100:
            raise ValueError("Brightness value must be an integer between 0 and 100!")

        self.brightness = brightness
        self.send_cmd(f"Dimmer {brightness}")

    def get_brightness(self, new_read: bool = False):
        if new_read:
            self.send_cmd("Dimmer")
            return read_response(self)['Dimmer']
        return self.brightness

    def set_color(self, color: str):
        self.color = color
        self.send_cmd(f"Color {color}")

    def get_color(self, new_read: bool = False):
        if new_read:
            self.send_cmd("Color")
            return read_response(self)['Color']
        return self.color

    def set_channels(self, r: int, g: int, b: int):
        if \
                not isinstance(r, int) or r < 0 or r > 100 \
                        or not isinstance(g, int) or g < 0 or g > 100 \
                        or not isinstance(b, int) or b < 0 or b > 100:
            raise ValueError("Channel values must be integers between 0 and 100!")

        self.send_cmds(f"Channel1 {r}", f"Channel2 {g}", f"Channel3 {b}")
        self.channels = [r, g, b]

    # HueSaturationBrightness
    def set_hsb(self, hsb: list):
        if \
                not isinstance(hsb[0], int) or hsb[0] < 0 or hsb[0] > 100 \
                        or not isinstance(hsb[1], int) or hsb[1] < 0 or hsb[1] > 100 \
                        or not isinstance(hsb[2], int) or hsb[2] < 0 or hsb[2] > 100:
            raise ValueError("HSB values must be integers between 0 and 100!")

        self.hue = hsb[0]
        self.saturation = hsb[1]
        self.brightness = hsb[2]

        self.send_cmd(f"HSBColor {hsb}")

        resp = read_response(self)
        self.save_resp_data(resp)

    # HueSaturationBrightness
    def get_hsb(self, new_read: bool = False):
        if new_read:
            self.send_cmd("HSBColor")
            resp = read_response(self)

            self.save_resp_data(resp)
            return resp['HSBColor']
        return self.hue, self.saturation, self.brightness

    def save_resp_data(self, data: dict):
        try:
            self.power = bool(1 if data['POWER'] == "ON" else 0)
        except KeyError:
            return

        try:
            self.color = data['Color']
        except KeyError:
            return

        try:
            hsb = data['HSBColor'].split(",")
            self.hue = int(hsb[0])
            self.saturation = int(hsb[1])
            self.brightness = int(hsb[2])
        except KeyError:
            print(f"HSBColor Keyerror! Data: {data}")
            return
        except IndexError:
            print(f"hsb IndexError! Data: {hsb}")
            return

    def __del__(self):
        self.set_brightness(0)
        self.conn.close()
