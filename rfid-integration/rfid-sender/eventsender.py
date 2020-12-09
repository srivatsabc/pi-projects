#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import logging
import msal
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..', 'myHttpTrigger')))
import app_config
import requests
import json

print('\n')
print("Waiting for item scan ...")
print('\n')
while (True):
	reader = SimpleMFRC522()

	try:
		(id, text) = reader.read()
		print ("Scan Detected")
		print ("item code : " + str(id))
		print ("item details : " + text)
		print("Connecting to Azure AD for token ")
		
		app = msal.ConfidentialClientApplication(app_config.CLIENT_ID,
				authority=app_config.AUTHORITY,
				client_credential=app_config.CLIENT_SECRET)
		result = None
		if not result:
			result = app.acquire_token_for_client(scopes=app_config.SCOPE)
			print("Got token : " + str(result['access_token']))			
		#data = json.dumps(text)
		#logging.info('msg ' + str(data))
		print("Sending item to event hubs ")
		eventhub_api_response = requests.post(app_config.WRITE_ENDPOINT,
									data=text,
									headers={'Authorization': 'Bearer ' + result['access_token'], 
									'Content-Type': 'application/atom+xml;type=entry;charset=utf-8'
								})
		print('Send response : ' + str(eventhub_api_response))
		print('\n')
		print('Waiting for next scan ...')
		print('\n')
	finally:
		GPIO.cleanup()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(app_config.CLIENT_ID,
            authority=authority or app_config.AUTHORITY,
            client_credential=app_config.CLIENT_SECRET,
            token_cache=cache)
