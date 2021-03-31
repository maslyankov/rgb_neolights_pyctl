from neolights_ctl import NeoLightsCtl
from time import sleep
from vendor.luxmeters.ut382.ut382 import list_ports


def int_to_str(num):
    num = str(num).ljust(2, '0')
    return num


def cycle_colors(lightctl):
    for red in range(0, 255):
        for green in range(0, 255):
            for blue in range(0, 255):
                red_hex = format(red, 'X').ljust(2, '0')
                green_hex = format(green, 'X').ljust(2, '0')
                blue_hex = format(blue, 'X').ljust(2, '0')

                color_hex = f"{red_hex}{green_hex}{blue_hex}"

                if blue % 9 == 0:
                    print(f"Setting color {color_hex}")

                    lightctl.set_color(color_hex)
                    sleep(1)


def main():
    list_ports()

    lights_ctl = NeoLightsCtl()
    print("Starting sequence")

    # for x in range(0, 5):
    #     lights_ctl.set_brightness(20 * x)
    #     sleep(1)
    #
    lights_ctl.set_brightness(0)

    # some_color = '009000'
    #
    # for pixel in range(lights_ctl.pixels_count, 0, -1):
    #     print(f"setting pixel {pixel}")
    #     lights_ctl.set_led(pixel, some_color)
    #     sleep(1.5)

    # Cycle colors
    lights_ctl.set_brightness(0)

    # lights_ctl.set_brightness(60)

    # cycle_colors(lights_ctl)


if __name__ == "__main__":
    main()
