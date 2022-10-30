import random
import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message, MethodResponse
import serial
from pydblite.sqlite import Database, Table
from dblite import in_mem_cache
import json 

# Set up cache 
cache = in_mem_cache()

# Set connection string
CONNECTION_STRING = "HostName=iothubmaznadev01.azure-devices.net;DeviceId=raspberry01;SharedAccessKey=AtAxA4c8etxnYNwz9RhdLDy+8kdIyNNM6HFKaovs9VU="

INTERVAL = 1

def create_client():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

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


async def run_telemetry_sample(client):
    print("IoT Hub device sending periodic messages")

    await client.connect()
    id = None
    while True:
        id = read_rfid()
        if id != None:
            # Get item from cache
            item = cache.get(str(id))
            message = Message(json.dumps(item))

            # Send the message.
            print("Sending message: {}".format(message))
            await client.send_message(message)
            print("Message sent")


def main():
    # Instantiate the client
    client = create_client()

    loop = asyncio.get_event_loop()
    try:
        # Run the sample in the event loop
        loop.run_until_complete(run_telemetry_sample(client))
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped by user")
    finally:
        # Upon application exit, shut down the client
        print("Shutting down IoTHubClient")
        loop.run_until_complete(client.shutdown())
        loop.close()

def read_rfid ():
   ser = serial.Serial ("/dev/ttyS0")                           
   ser.baudrate = 9600                                           
   data = ser.read(12)                                            
   ser.close ()                                                   
   data=data.decode("utf-8")
   return data                                                    

if __name__ == '__main__':
    main()