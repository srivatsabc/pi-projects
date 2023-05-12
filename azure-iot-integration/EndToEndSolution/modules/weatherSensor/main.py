# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message, MethodResponse
import json 
import bme680
import os, time

# Event indicating client stop
stop_event = threading.Event()

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

print('Calibration data:')
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print('{}: {}'.format(name, value))

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print('\n\nInitial reading:')
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print('{}: {}'.format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

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
    print("IoT Weather Station device sending periodic messages")

    await client.connect()
    try:
        while True:
            if sensor.get_sensor_data():
                msg = {}
                msg ["temperature"] = float("{:.2f}".format(sensor.data.temperature))
                msg ["pressure"] = float("{:.2f}".format(sensor.data.pressure))
                msg ["humidity"] = float("{:.2f}".format(sensor.data.humidity))

                if sensor.data.heat_stable:
                    msg ["gas"] = float(sensor.data.gas_resistance)

                message = Message(json.dumps(msg), content_encoding="utf-8", content_type="application/json")
                message.custom_properties["transaction_type"] = "weather_station"
                # Send the message.
                print("Sending message: {}".format(message))
                await client.send_message_to_output(message, "input1")
                print("Message sent to dispatcher")
            time.sleep(int(os.getenv('WAIT_TIME')))

    except KeyboardInterrupt:
        pass           

def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "Weather Station client" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("Weather Station client stopped by edge")
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

if __name__ == "__main__":
    main()
