from gpiozero import MotionSensor
import time

pir = MotionSensor(4)
while True:
    pir.wait_for_motion()
    if pir.motion_detected:
        print("Motion Detected")
        time.sleep(5)
    else:
        print('No motion')
    pir.wait_for_no_motion()