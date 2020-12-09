#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        reader.write("{\"comments\": \"pant\", \"age\": 5, \"gender\": \"male\"}")
        print("Written")
finally:
        GPIO.cleanup()
