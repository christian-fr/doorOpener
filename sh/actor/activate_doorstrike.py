import sys
import time
import RPi.GPIO as GPIO

DOORSTRIKE = 17


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(DOORSTRIKE, GPIO.OUT)
    GPIO.output(DOORSTRIKE, 0)
    time.sleep(6)
    GPIO.output(DOORSTRIKE, 1)
    time.sleep(4)
    sys.exit(0)


if __name__ == '__main__':
    main()
