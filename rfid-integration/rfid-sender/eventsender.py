#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import logging
import msal
import sys
import os
import app_config
import requests
import json
import geocoder
import random
print('\n')
while (True):
	print("Waiting for item scan ...")
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
			#print("Got token : " + str(result['access_token']))			
		geo_location = geocoder.ip("me")
		
		msg = {}
		rfid = str(text.rstrip()).split(',')
		msg["container_id"] = rfid[0]
		msg["latitude"] = float(rfid[1])
		msg["longitude"] = float(rfid[2])
		msg["origin_id"] = "N"
		msg["destination_id"] = "N"
		msg["status"] = "InProgress"
		print('msg ' + str(json.dumps(msg)))
		print("Sending item to event hubs ")
		eventhub_api_response = requests.post(app_config.WRITE_ENDPOINT,
			data=json.dumps(msg),
			headers={'Authorization': 'Bearer ' + result['access_token'], 
			'Content-Type': 'application/atom+xml;type=entry;charset=utf-8'
		})
		print('Send response : ' + str(eventhub_api_response))
		print('\n')
		print('Waiting for next item scan ...')
		print('\n')
	finally:
		GPIO.cleanup()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(app_config.CLIENT_ID,
            authority=authority or app_config.AUTHORITY,
            client_credential=app_config.CLIENT_SECRET,
            token_cache=cache)
