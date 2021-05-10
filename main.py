from time import sleep

from neolights_ctl import NeoLightsCtl
from luxmeters.serial_utils import list_ports
from luxmeters.Sensor import Sensor


def int_to_str(num):
    num = str(num).ljust(2, '0')
    return num


class TestLights:
    def __init__(self, sensor, light):
        print(f"Initialising Test measurement")

        if not sensor:
            raise ValueError("Sensor is required!")
        self.sensor = sensor

        if not light:
            raise ValueError("Light is required!")
        self.light = light

        self.measurements = list()

    def grab_data(self, color):
        data = self.sensor.get('delta_uv')

        self.measurements.append({
            "color_hex": color,
            "EV": data[0],
            "TCP": data[1],
            "deltaUV": data[2]
        })

    def cycle_colors(self, action):
        self.light.set_brightness(90)

        test_counter = 0

        for red in range(0, 255):
            for green in range(0, 255):
                for blue in range(1, 255):
                    if test_counter > 10:
                        break

                    red_hex = format(red, 'X').ljust(2, '0')
                    green_hex = format(green, 'X').ljust(2, '0')
                    blue_hex = format(blue, 'X').ljust(2, '0')

                    color_hex = f"{red_hex}{green_hex}{blue_hex}"

                    if blue % 9 == 0:
                        print(f"Setting color {color_hex}")

                        self.light.set_color(color_hex)
                        sleep(.5)

                        # After change do...
                        if action and self.sensor:
                            action(color=color_hex)

                        test_counter += 1
                        sleep(.5)
                    else:
                        print(f"Skipping {color_hex}...")

    def __del__(self):
        print("exiting...")
        print(f"Measured data: {self.measurements}")


def main():
    print(list_ports())

    light = NeoLightsCtl()

    s = Sensor(model="cl200a")

    print(s.get('all'))

    testing = TestLights(sensor=s, light=light)

    try:
        testing.cycle_colors(testing.grab_data)
    except KeyboardInterrupt:
        exit(0)

    # for x in range(0, 5):
    #     lights_ctl.set_brightness(20 * x)
    #     sleep(1)
    #
    # lights_ctl.set_brightness(0)

    # some_color = '009000'
    #
    # for pixel in range(lights_ctl.pixels_count, 0, -1):
    #     print(f"setting pixel {pixel}")
    #     lights_ctl.set_led(pixel, some_color)
    #     sleep(1.5)

    # Cycle colors
    # lights_ctl.set_brightness(0)

    # lights_ctl.set_brightness(60)

    # cycle_colors(lights_ctl)


if __name__ == "__main__":
    main()
