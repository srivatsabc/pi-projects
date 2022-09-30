import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
rfid = SimpleMFRC522()
try:
        print("Hold tag near the module...")
        rfid.write("Container-X018792,39.09,-94.57")
        print("Written")
finally:
        GPIO.cleanup()
