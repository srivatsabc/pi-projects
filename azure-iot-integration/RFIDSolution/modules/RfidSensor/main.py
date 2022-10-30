# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message, MethodResponse
import serial
from dblite import in_mem_cache
import json 

# Event indicating client stop
stop_event = threading.Event()

# Set up cache 
cache = in_mem_cache()

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define a method request handler
    async def method_request_handler(method_request):
        if method_request.name == "SetTelemetryInterval":
            try:
                global INTERVAL
                INTERVAL = int(method_request.payload)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse.create_from_method_request(method_request, response_status, response_payload)
        await client.send_method_response(method_response)

    try:
        # Attach the method request handler
        client.on_method_request_received = method_request_handler
    except:
        # Clean up in the event of failure
        client.shutdown()
        raise

    return client


async def run_telemetry_send(client):
    print("IoT Hub device sending periodic messages")

    await client.connect()
    id = None
    while True:
        id = read_rfid()
        if id != None:
            # Get item from cache
            item = cache.get(str(id))
            message = Message(json.dumps(item), content_encoding="utf-8", content_type="application/json")
            message.custom_properties["transaction_type"] = item["type"]
            # Send the message.
            print("Sending message: {}".format(message))
            await client.send_message_to_output(message, "input1")
            print("Message sent to dispatcher")

def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "Sender IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("Sender IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_telemetry_send(client))
    except Exception as e:
        print("Sender Unexpected error %s " % e)
        raise
    finally:
        print("Sender Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()

def read_rfid ():
   ser = serial.Serial ("/dev/ttyS0")                           
   ser.baudrate = 9600                                           
   data = ser.read(12)                                            
   ser.close ()                                                   
   data=data.decode("utf-8")
   return data             

if __name__ == "__main__":
    main()
