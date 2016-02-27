# -*- coding: utf-8 -*-
import time
import json

# Relayr Imports
from relayr import Client
from relayr import dataconnection as dc
from relayr import resources

def main():
    """
    A demo to show the usage of the mqtt queuing functionality of the Relayr SDK.

    This is also an example of monitoring all devices of a user, and could serve
        as the basis of a custom dashboard in Flask, etc.
    """

    # Add your app token here
    YOUR_APP_TOKEN = "" # Leave out the "Bearer "

    print("Connecting to the Cloud...")
    client = Client(token=YOUR_APP_TOKEN)
    user_id = client.api.get_oauth2_user_info()['id']

    print("Gathering All User Devices...")
    devices_json = client.api.get_user_devices(user_id)
    devices = [resources.Device(id=d['id'], client=client) for d in devices_json]
    print("{} devices found.".format(len(devices)))

    # Use if you want extended data, such as name, description, etc.
    print("Gathering Device Data...")
    for device in devices:
        device.get_info()

    print("Starting MQTT Stream...")
    mqtt = dc.MqttStream(callback=None,    # A callback of "None" will queue messages as they are recieved.
                         devices=devices)
    mqtt.start()

    print("Started.")
    while True:
        time.sleep(1)
        for msg in mqtt.get_messages():
            print(get_device_name(devices, msg.payload), resources_simplifier(msg.payload))

# Helper Functions
def resources_simplifier(payload):
    x = json.loads(payload.decode())
    out = {}
    for i in x['readings']:
        out[i['meaning']] = i['value']
    return out

def get_device_name(devices, payload):
    x = json.loads(payload.decode())
    for device in devices:
        if x['deviceId'] == device.id:
            return device.name

    # No matching device was found
    raise Exception()

if __name__ == '__main__':
    main()
