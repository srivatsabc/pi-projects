from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import uuid
from cachetools import cached, TTLCache
import configs
import logging 
import sys
import traceback
import os
import msal
import requests
from requests_toolbelt import MultipartEncoder

# Setup logging
logger = logging.getLogger("logging_tryout2")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Method to get jwt token for accessing the ML api
@cached(cache=TTLCache(maxsize=1, ttl=3500))
def get_ad_token(scope=configs.SCOPE):
  app = msal.ConfidentialClientApplication(os.environ.get('CLIENT_ID'),
          authority=configs.AUTHORITY,
          client_credential=os.environ.get('CLIENT_SECRET'))
  result = None
  if not result:
    result = app.acquire_token_for_client(scopes=scope)
    return result['access_token']

# Method to capture images from Rpi camera
def capture_image():
  picam = Picamera2()
  config = picam.create_preview_configuration()
  picam.configure(config)
  picam.start()
  picam.exposure_mode = 'beach'
  picam.awb_mode = 'sunlight'
  sleep(2)
  image = f"images/camera_caputure_{str(uuid.uuid4())}.jpg"
  picam.capture_file(image)
  picam.close()
  return image

def predict(image):
  # Get token
  token = get_ad_token()

  # Create the multipart payload
  mp_encoder = MultipartEncoder(
    fields={
        'file': ("image", open(image, 'rb'), 'multipart/form-data')
    }
  )

  # Call the ML api for predictions
  response = requests.post(configs.ML_ENDPOINT,
    data=mp_encoder,
    headers={'Authorization': 'Bearer ' + token,
            'Content-Type': mp_encoder.content_type
            }
  )
  
  if response.status_code != 200:
    raise Exception
  else:
    response = response.json()
    logger.info(f"Class: {response['class']}")
    if response['class'] == configs.CLASS_OK:
      os.remove(image)
    return response

# GPIO warmup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN)
sleep(10)

# Loop to monitor PIR motion sensor 
while True:
 i = GPIO.input(12)
 if i==1:
  logger.info("Motion detected")
  try:
    # Capture images
    image = capture_image()

    # Run predictions
    predictions = predict(image)
  except:
      logger.info("Exception: " + str(sys.exc_info()[0]))
      traceback.print_exc()
  sleep(5)
