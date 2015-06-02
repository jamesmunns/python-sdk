#!/usr/bin/python

"""
Example script accessing data from a WunderBar sensor via MQTT.

This will connect to the MQTT server and wirte the sensor data
to an ODBC server.

Please, maintain access data in odbclogger_ini.py.
"""

import json
import sys
import time

import pyodbc
from relayr import Client
from relayr.resources import Device
from relayr.dataconnection import MqttStream

# Include properties file.
from odbclogger_ini import *


# Check that all properties needed are set.
try:
    settings = [ACCESS_TOKEN, SENSOR_ID, ODBC_DSN]
    assert not any(map(lambda x: x=='', settings))
except AssertionError:
    print('Please, provide values in file odbclogger_ini.py.')
    sys.exit(1)

class Callbacks(object):
    "A class providing callbacks for incoming data from some device."

    def __init__(self, device, cursor):
        "Constructor."
        self.device = device
        self.cursor = cursor

    def sensor(self, topic, message):
        "Callback to log sensor data to SQL database."

        readings = json.loads(message)['readings']
        sql = 'INSERT INTO wunderdata (device, sensor, value) VALUES (?, ?, ?)'
        sys.stdout.write(self.device.name + ': ')
        for r in readings:
            obj = r['value']
            if isinstance(obj, float):
                self.cursor.execute(sql, \
                    self.device.name, r['meaning'], obj).commit()
                sys.stdout.write( r['meaning'] + ' = ' + str(obj) + '; ')
            if isinstance(obj, dict):
                for k, v in obj.items():
                    self.cursor.execute(sql, \
                        self.device.name, r['meaning'] + '-' + k, v).commit()
                    sys.stdout.write( r['meaning'] + '-' + k + ' = ' + str(v) + '; ')
        sys.stdout.write('\n')

def connect():
    "Connect to a device and read data until interrupted by CTRL+C."

    DSN = 'DSN=' + ODBC_DSN
    if ODBC_USER:
        DSN += ';UID=' + ODBC_USER
    if ODBC_PASSWORD:
        DSN += ';PWD=' + ODBC_PASSWORD

    # Connect to dtabase.
    cnxn = pyodbc.connect(DSN)
    cursor = cnxn.cursor()

    print("Connected to database")

    try:
        # Check if database table already exists.
        cursor.execute("SELECT id, time, sensor, value FROM wunderdata")
    except: # catch all
        cursor.execute("""
            CREATE TABLE wunderdata (
              id     INT NOT NULL AUTO_INCREMENT,
              device CHAR(40) NOT NULL,
              sensor CHAR(20) NOT NULL,
              time   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              value  float NOT NULL,
              PRIMARY KEY (id),
              KEY data (device, sensor, time)
              )""" )
        cursor.commit()

    c = Client(token=ACCESS_TOKEN)
    device = Device(id=SENSOR_ID, client=c).get_info()
    callbacks = Callbacks(device, cursor)
    print("Monitoring '%s' (%s) ..." % (device.name, device.id))
    try:
        # Loop until interrupted by keyboard.
        while True:
            stream = MqttStream(callbacks.sensor, [device], transport='mqtt')
            stream.start()
            time.sleep(10)
            stream.stop()
    except KeyboardInterrupt:
        print('')
        stream.stop()
    print("Stopped")

    # Close database connection.
    cnxn.close()

# Entry point.
if __name__ == "__main__":
    connect()
