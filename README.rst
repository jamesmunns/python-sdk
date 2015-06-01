The relayr Python Library
=========================

Welcome to the relayr Python Library. The repository provides Python
developers with programmatic access points to the relayr_ platform
for the Internet of Things.

These include access to the relayr cloud via the relayr API_ as well as 
direct connection to the relayr WunderBar sensors, via Bluetooth Low
Energy (using BlueZ_ on Linux, still very experimental).


Installation
--------------

You can install the library using one of the following methods, using
``pip``:

1. You can either download the very latest version of the repository
   from GitHub::

      pip install git+https://github.com/relayr/python-sdk

2. or you install the latest package release from the
   `Python Package Index`_ as follows::

      pip install relayr

A more detailed description of how to install this package using Python
virtual environments and/or ``pip`` itself can be found in the manual,
see the ``docs/manual`` folder of the code distribution.


Examples
--------

Receive live data
.................

Receive a 10 second data stream using MQTT_, from one of your WunderBar sensors
(device). In the following example the device does not have to be a public one
in order to be used (you can obtain your device IDs from the relayr Dashboard
`My Devices`_ section):

.. code-block:: python

    import time
    from relayr import Client
    from relayr.dataconnection import MqttStream
    c = Client(token='<my_access_token>')
    dev = c.get_device(id='<my_device_id>')
    def mqtt_callback(topic, payload):
        print('%s %s' % (topic, payload))
    stream = MqttStream(mqtt_callback, [dev])
    stream.start()
    time.sleep(10)
    stream.stop()
    
PLEASE NOTE: Receiving data via MQTT will work only for Python versions 2.7
and above due to limited support in ``paho-mqtt`` for TLS in Python 2.6.
Also: the old style of receiving data via PubNub_ has been removed from
the relayr API_ and this code base.


Switch a device's LED on/off
............................

.. code-block:: python

    from relayr import Client
    c = Client(token='<my_access_token>')
    d = c.get_device(id='<my_device_id>')
    d.switch_led_on(True)

You can find more examples in the ``demos`` directory of the unarchived
source code distribution or online in the `demos folder on GitHub`_.


Documentation
-------------

For references to the full documentation for the Python library please visit
our Developer Dashboard `Python section`_!


.. comment:
    .. include:: CHANGELOG.txt


.. _relayr: https://relayr.io
.. _repository: https://github.com/relayr/python-sdk
.. _API: https://developer.relayr.io/documents/relayrAPI/Introduction
.. _Python Package Index: https://pypi.python.org/pypi/relayr/
.. _BlueZ: http://www.bluez.org/
.. _Python section: https://developer.relayr.io/documents/Python/Introduction
.. _My Devices: https://developer.relayr.io/dashboard/devices
.. _PubNub: http://www.pubnub.com/
.. _MQTT: http://mqtt.org/
.. _demos folder on GitHub: https://github.com/relayr/python-sdk/tree/master/demos
