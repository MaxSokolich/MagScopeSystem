from adafruit_motorkit import MotorKit
import time

kit = MotorKit()

kit.motor1.throttle = -1
time.sleep(3)
kit.motor1.throttle = 0 