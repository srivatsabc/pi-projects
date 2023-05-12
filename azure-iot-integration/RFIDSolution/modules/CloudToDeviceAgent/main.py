import time
from azure.iot.device import IoTHubDeviceClient

CONNECTION_STRING = "HostName=iothubmaznadev01.azure-devices.net;DeviceId=raspberry01;SharedAccessKey=9JRA7Yfzb61cN64Z/PrV8QUB8wP2kZbdvSHlhrbts7s="

def message_handler(message):
    print("Message received from cloud")
    print(message.data.decode('utf-8'))
    print(message.custom_properties)

def main():
    # Instantiate the client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    print ("Waiting for C2D messages")
    try:
        # Attach the handler to the client
        client.on_message_received = message_handler

        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("raspbery01 C2D messaging stopped")
    finally:
        # Graceful exit
        print("Shutting down IoT Hub Client")
        client.shutdown()

if __name__ == '__main__':
    main()