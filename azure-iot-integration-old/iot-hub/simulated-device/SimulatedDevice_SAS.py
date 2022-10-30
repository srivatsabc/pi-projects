import base64
import hashlib
import urllib
import hmac
import requests
import json
import time
import psutil

# Azure IoT Hub
HOST_NAME = 'ENTER_YOUR_HOST_NAME'
DEVICE_ID = 'ENTER_YOUR_DEVICE_ID'
SHARED_ACCESS_KEY = 'ENTER_YOUR_SHARED_ACCESS_KEY'

# Programmatically generate a SAS token for using the IoT Hub REST APIs
# https://docs.microsoft.com/en-us/rest/api/eventhub/generate-sas-token
def generate_sas_token():
    expiry=3600
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((urllib.parse.quote_plus(HOST_NAME)), int(ttl))
    signed_hmac_sha256 = hmac.HMAC(base64.b64decode(SHARED_ACCESS_KEY), sign_key.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(signed_hmac_sha256.digest())
    rawtoken = {
        'sr' :  HOST_NAME,
        'sig': signature,
        'se' : str(int(ttl))
    }
    return 'SharedAccessSignature ' + urllib.parse.urlencode(rawtoken)

# Send data to IoT Hub
def send_message(token, message):
    url = 'https://{0}/devices/{1}/messages/events?api-version=2018-04-01'.format(HOST_NAME, DEVICE_ID)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    data = json.dumps(message)
    requests.post(url, data=data, headers=headers)

if __name__ == '__main__':
    # 1. Generate SAS Token
    token = generate_sas_token()

    # 2. Simulate IoT Device
    while True:
        datapoint = psutil.cpu_percent()
        print(datapoint)
        message = {"cpu": datapoint}
        send_message(token, message)
        time.sleep(1)
