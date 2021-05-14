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

    def grab_data(self, color=None, hsb=None):
        data = self.sensor.get('delta_uv')
        if data[1] < 0:
            return -1

        new_data = {
            "EV": data[0],
            "TCP": data[1],
            "deltaUV": data[2]
        }

        if color:
            new_data["color_hex"] = color
        if hsb:
            new_data["hsb"] = hsb

        print(f"Measured: {new_data}")
        self.measurements.append(new_data)

    def go_through_colors_list(self, action=None, colors_list: list):
        test_counter = 0
        colors_num = len(colors_list)

        print()
        print("------------------------------")
        print(f"Starting colors list... ({colors_num} tests)")

        for color in colors_list:
            print(f"Setting color {color}")

            self.light.set_color(color)
            print("Waiting 1.5 sec for the sensor to load...")
            sleep(1.5)

            # After change do...
            res = 1
            if action and self.sensor:
                res = action(color=color)

            if res != -1:
                test_counter += 1
                print(f"Test {test_counter}/{colors_num} saved")
            else:
                print("Results are not logical! Not counting this test!")

            sleep(.5)

        print("List ended!")
        print("------------------------------")

    def cycle_colors(self, action=None):
        # self.light.set_brightness(100)
        test_counter = 0
        tests_num = 0  # 0 for infinite

        print()
        print("------------------------------")
        print(f"Starting colors cycle... ({tests_num-1 if tests_num else 'infinite'} tests)")

        for blue in range(150, 255):
            for green in range(150, 255):
                for red in range(150, 255):
                    if tests_num != 0 and test_counter > tests_num:
                        break

                    red_hex = format(red, 'X').ljust(2, '0')
                    green_hex = format(green, 'X').ljust(2, '0')
                    blue_hex = format(blue, 'X').ljust(2, '0')

                    color_hex = f"{red_hex}{green_hex}{blue_hex}"

                    # if blue % 9 == 0:
                    print(f"Setting color {color_hex}")

                    self.light.set_color(color_hex)
                    print("Waiting 1.5 sec for the sensor to load...")
                    sleep(1.5)

                    # After change do...
                    res = 1
                    if action and self.sensor:
                        res = action(color=color_hex)

                    if res != -1:
                        test_counter += 1

                        print(f"Test {test_counter}/{tests_num} saved")
                    else:
                        print("Results are not logical! Not counting this test!")

                    sleep(.5)
                    # else:
                    #     print(f"Skipping {color_hex}...")

        print("Cycling ended!")
        print("------------------------------")

    def cycle_hsb(self, action=None):
        test_counter = 0
        tests_num = 0  # 0 for infinite

        print()
        print("------------------------------")
        print(f"Starting colors cycle... ({tests_num-1 if tests_num else 'all'} tests)")

        target_brightness = 100

        for hue in range(0, 100):
            for saturation in range(0, 100):
                if tests_num != 0 and test_counter > tests_num:
                    break

                hsb = [hue, saturation, target_brightness]

                # if blue % 9 == 0:
                print(f"Setting hsb to [{hue}, {saturation}, {target_brightness}]")

                self.light.set_hsb(hsb)
                print("Waiting 1.5 sec for the sensor to load...")
                sleep(1.5)

                # After change do...
                res = 1
                if action and self.sensor:
                    res = action(hsb=hsb)

                if res != -1:
                    test_counter += 1

                    print(f"Test {test_counter}/{tests_num} saved")
                else:
                    print("Results are not logical! Not counting this test!")

                sleep(.5)

        print("Cycling ended!")
        print("------------------------------")

    def __del__(self):
        print("exiting...")
        print(f"Measured data: \n{self.measurements}")
        measured_colors = [d['color_hex'] for d in self.measurements if 'color_hex' in d]
        print(f"colors list: \n{measured_colors}")


def main():
    print(list_ports())

    light = NeoLightsCtl()

    light.set_brightness(100)

    s = Sensor(model="cl200a")

    print(s.get('all'))

    testing = TestLights(sensor=s, light=light)

    colors_list = ['969696', 'D79696', 'D89696', 'D99696', 'DA9696', 'DB9696', 'DC9696', 'DD9696', 'DE9696', 'DF9696', 'E09696', 'E19696', 'E29696', 'E39696', 'E49696', 'E59696', 'E69696', 'E79696', 'E89696', 'E99696', 'EA9696']
    testing.go_through_colors_list(testing.grab_data, colors_list)

    # testing.cycle_colors(testing.grab_data)


if __name__ == "__main__":
    main()
