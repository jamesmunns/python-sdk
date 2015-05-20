# -*- coding: utf-8 -*-

"""
Data Connection Classes

This module provide connection classes for accessing device data.
"""

import sys
import ssl
import time
import threading

import requests
import certifi
import paho.mqtt.client as mqtt

from relayr import config
from relayr.compat import PY2, PY3


class MqttStream(threading.Thread):
    "MQTT stream reading data from devices in the relayr cloud."

    def __init__(self, callback, devices, transport='mqtt'):
        """
        Opens an MQTT connection with a callback and one or more devices.

        :param callback: A callable to be called with two arguments:
            the topic and payload of a message.
        :type callback: A function/method or object implementing the ``__call__`` method.
        :param devices: Device objects from which to receive data.
        :type devices: list
        :param transport: Name of the transport method, right now only 'mqtt'.
        :type transport: string
        """
        super(MqttStream, self).__init__()
        self._stop_event = threading.Event()
        self.callback = callback
        self.credentials_list = [dev.create_channel(transport)
            for dev in devices]
        self.topics = [credentials['credentials']['topic']
            for credentials in self.credentials_list]
        self.setDaemon(True)

    def run(self):
        """
        Thread method, called implicitly after starting the thread.
        """
        creds = self.credentials_list[0]['credentials']
        c = self.client = mqtt.Client(client_id=creds['clientId'])
        c.on_connect = self.on_connect
        c.on_disconnect = self.on_disconnect
        c.on_message = self.on_message
        c.on_subscribe = self.on_subscribe
        c.on_unsubscribe = self.on_unsubscribe
        c.username_pw_set(creds['user'], creds['password'])
        c.tls_set(certifi.where(), tls_version=ssl.PROTOCOL_TLSv1)
        c.connect(config.RELAYR_MQTT_HOST, port=config.RELAYR_MQTT_PORT, keepalive=60)

        try:
            c.loop_forever()
        except KeyboardInterrupt:
            self.stop()

        while not self._stop_event.is_set():
            time.sleep(1)

    def stop(self):
        """
        Mark the connection/thread for being stopped.
        """
        if not self._stop_event.is_set():
            for t in self.topics:
                if PY2:
                    t = t.encode('utf-8')
                self.client.unsubscribe(t)
        self._stop_event.set()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if not self._stop_event.is_set():
            for t in self.topics:
                if PY2:
                    t = t.encode('utf-8')
                self.client.subscribe(t)

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_unsubscribe(self, client, userdata, mid):
        pass

    def on_message(self, client, userdata, msg):
        """
        Pass the message topic and payload as strings to our callback.
        """
        if PY2:
            self.callback(msg.topic, msg.payload)
        else:
            self.callback(msg.topic, msg.payload.decode("utf-8"))

    def add_device(self, device):
        "Add a specific device to the MQTT connection to receive data from."
        # create credentials
        creds = device.create_channel('mqtt')
        self.credentials_list.append(creds)
        # extract topic
        topic = creds['credentials']['topic']
        self.topics.append(topic)
        # subscribe topic
        if PY2:
           topic = topic.encode('utf-8')
        self.client.subscribe(topic)

    def remove_device(self, device):
        "Remove a specific device from the MQTT connection to no longer receive data from."
        # find respective credentials
        dummy_creds = device.create_channel('mqtt')
        creds = [c for c in self.credentials_list
            if c['credentials']['topic'] == dummy_creds['credentials']['topic']][0]
        # remove from self.credentials_list and self.topics
        self.credentials_list.remove(creds)
        topic = creds['credentials']['topic']
        self.topics.remove(topic)
        # unsubscribe topic
        if PY2:
           topic = topic.encode('utf-8')
        self.client.unsubscribe(topic)
