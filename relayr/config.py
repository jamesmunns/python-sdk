# -*- coding: utf-8 -*-

"""
A set of configuration variables used for various purposes.

This module provides defaults for configuration variables and a way
of overwriting these from the shell environment or a script using
the relayr client.
"""

import os
import platform

from .version import __version__


# defaults
relayrAPI = 'https://api.relayr.io'
clientName = 'io.relayr.sdk.python'
userAgentString = '{client_name}/{client_version} '
userAgentString += '({platform}; {arch}; {python_implementation}-{python_version})'
DEBUG = False
LOG = False
LOG_DIR = os.getcwd()
RELAYR_FOLDER = os.path.expanduser('~/.relayr')
RELAYR_MQTT_HOST = 'mqtt.relayr.io'
RELAYR_MQTT_PORT = 8883

# overwrite with environment variables if given
relayrAPI = os.environ.get('RELAYR_API', relayrAPI)
clientName = os.environ.get('RELAYR_PYTHON_CLIENT_NAME', clientName)
userAgentString = os.environ.get('RELAYR_DATAHUB', userAgentString)
DEBUG = True if os.environ.get('RELAYR_DEBUG', 'False') == 'True' else False
LOG = True if os.environ.get('RELAYR_LOG', 'False') == 'True' else False
LOG_DIR = os.environ.get('RELAYR_LOG_DIR', LOG_DIR)
RELAYR_FOLDER = os.environ.get('RELAYR_FOLDER', RELAYR_FOLDER)
RELAYR_MQTT_HOST = os.environ.get('RELAYR_MQTT_HOST', RELAYR_MQTT_HOST)
RELAYR_MQTT_PORT = int(os.environ.get('RELAYR_MQTT_PORT', RELAYR_MQTT_PORT))

# derived variable, HTTP user-agent string
userAgent = userAgentString.format(
	client_name=clientName,
	client_version=__version__,
	platform=platform.system() + '-' + platform.release(),
	arch=platform.machine() + '-' + platform.architecture()[0],
	python_implementation=platform.python_implementation(),
	python_version=platform.python_version(),
)

del os, platform
