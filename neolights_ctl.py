from serial import Serial, SerialException
from time import sleep
from json import loads

from luxmeters.serial_utils import list_ports, find_all_luxmeters

# from vendor.luxmeters.konica.CL200A import CL200A


def _read_response(resp, obj):
    try:
        out = loads(resp.split(' = ')[1])
    except IndexError:
        try:
            print("Getting resp failed, retrying...")
            new_read = obj.read()
            out = loads(new_read.split(' = ')[1])
        except IndexError:
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
            exit(1)

        baud = 115200
        try:
            self.conn = Serial(device, baud)
        except SerialException:
            raise ValueError("Could not connect to serial device")

        print("Waiting 1 sec while initializing...")
        sleep(1)

        # self.set_brightness(20)

        self.pixels_count = self.get_pixels_count()
        print(f"Init pixels count = {self.pixels_count}")

        self.dimmer = self.get_brightness()
        print(f"Init dimmer = {self.dimmer}")

        self.color = self.get_color()
        print(f"Init color = {self.color}")

        # Turn Off Wifi
        self.send_cmd("Wifi 0")

    def read(self):
        return self.conn.read(self.conn.in_waiting).decode('ascii')

    def send_cmd(self, cmd):
        self.conn.write(f"{cmd}\n".encode())

    def get_pixels_count(self):
        self.send_cmd("Pixels")
        # sleep(2)
        return read_response(self)['Pixels']

    def set_led(self, led_num, color):
        self.send_cmd(f"Led{led_num} {color}")

    def set_brightness(self, brightness):
        self.dimmer = brightness
        self.send_cmd(f"Dimmer {brightness}")

    def get_brightness(self):
        self.send_cmd("Dimmer")
        return read_response(self)['Dimmer']

    def set_color(self, color):
        self.color = color
        self.send_cmd(f"Color {color}")

    def get_color(self):
        self.send_cmd("Color")
        return read_response(self)['Color']

    def __del__(self):
        self.set_brightness(0)
        self.conn.close()
