# -*- coding: utf-8 -*-

"""
This module contains abstractions for relayr API resources.

Resources may be entities such as users, publishers, applications, 
devices, device models and transmitters.
"""

import warnings

from relayr import exceptions
from relayr.dataconnection import MqttStream as Connection
from relayr.utils.misc import get_start_end, datetime_to_millis


class User(object):
    "A Relayr user."

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_publishers(self):
        "Return a generator of the publishers of the user."

        for pub_json in self.client.api.get_user_publishers(self.id):
            p = Publisher(pub_json['id'], client=self.client)
            for k in pub_json:
                setattr(p, k, pub_json[k])
            yield p

    def get_apps(self):
        "Returns a generator of the apps of the user."

        for app_json in self.client.api.get_user_apps(self.id):
            ## TODO: change 'app' field to 'id' in API?
            app = App(app_json['app'], client=self.client)
            app.get_info()
            yield app

    def get_transmitters(self):
        "Returns a generator of the transmitters of the user."

        for trans_json in self.client.api.get_user_transmitters(self.id):
            trans = Transmitter(trans_json['id'], client=self.client)
            trans.get_info()
            yield trans

    def get_devices(self):
        "Returns a generator of the devices of the user."

        for dev_json in self.client.api.get_user_devices(self.id):
            dev = Device(dev_json['id'], client=self.client)
            dev.get_info()
            yield dev

    def update(self, name=None, email=None):
        res = self.client.api.patch_user(self.id, name=name, email=email)
        for k in res:
            setattr(self, k, res[k])
        return self

    ## TODO: rename to 'registered_wunderbar_devices'?
    def register_wunderbar(self):
        """
        Returns registered Wunderbar devices (master and sensor modules).
    
        :rtype: A generator over the registered devices and one transmitter.
        """    
        res = self.client.api.post_user_wunderbar(self.id)
        for k, v in res.items():
            if 'model' in v:
                item = Device(res[k]['id'], client=self.client)
                item.get_info()
            else:
                item = Transmitter(res[k]['id'], client=self.client)
                item.get_info()
            yield item

    def remove_wunderbar(self):
        """
        Removes all Wunderbars associated with the user.
        """
        res = self.client.api.post_users_destroy(self.id)
        return res

    def get_bookmarked_devices(self):
        """
        Retrieves a list of bookmarked devices.

        :rtype: list of device objects
        """
        res = self.client.api.get_user_devices_bookmarks(self.id)
        for dev in res:
            d = Device(dev['id'], client=self.client)
            for k, v in dev.items():
                setattr(d, k, v)
            d.get_info()
            yield d

    def bookmark_device(self, device):
        res = self.client.api.post_user_devices_bookmark(self.id, device.id)

    def delete_device_bookmark(self, device):
        res = self.client.api.delete_user_devices_bookmark(self.id, device.id)
        return res


class Publisher(object):
    """
    A relayr publisher.

    A publisher has a few attributes, which can be updated. It can be
    registered to and deleted from the relayr platform. It can list all
    applications it has published on the relayr platform.
    """

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_apps(self, extended=False):
        """
        Get list of apps for this publisher.

        If the optional parameter ``extended`` is ``False`` (default) the 
        response will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` it will contain additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.

        :param extended: Flag indicating if the info should be extended.
        :type extended: booloean
        :rtype: A list of :py:class:`relayr.resources.App` objects.
        """

        func = self.client.api.get_publisher_apps
        if extended:
            func = self.client.api.get_publisher_apps_extended
        res = func(self.id)
        for a in res:
            app = App(a['id'], client=self.client)
            app.get_info(extended=extended)
            yield app


    def update(self, name=None):
        """
        Updates certain information fields of the publisher's.
        
        :param name: the user email to be set
        :type name: string
        """
        res = self.api.patch_publisher(self.id, name=name)
        for k in res:
            setattr(self, k, res[k])
        return self

    def register(self, name, id, publisher):
        """
        Adds the publisher to the relayr platform.

        :param name: the publisher name to be set
        :type name: string
        :param id: the publisher UID to be set
        :type id: string
        """
        raise NotImplementedError

    def delete(self):
        """
        Deletes the publisher from the relayr platform.
        """
        res = self.api.delete_publisher(self.id)


class App(object):
    """
    A relayr application.
    
    An application has a few attributes, which can be updated. It can be
    registered to and deleted from the relayr platform. it can be connected 
    to and disconnected from devices.
    """
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self, extended=False):
        """
        Get application info.
        
        If the optional parameter ``extended`` is ``False`` (default) the 
        result will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` it will contain additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.
        
        :param extended: flag indicating if the info should be extended
        :type extended: booloean
        :rtype: A dict with certain fields.
        """

        func = self.client.api.get_app_info
        if extended:
            func = self.client.api.get_app_info_extended
        res = func(self.id)
        for k in res:
            setattr(self, k, res[k])
        return self

    def update(self, description=None, name=None, redirectUri=None):
        """
        Updates certain fields in the application's description.
        
        :param description: the user name to be set
        :type description: string
        :param name: the user email to be set
        :type name: string
        :param redirectUri: the redirect URI to be set
        :type redirectUri: string
        """
        res = self.client.api.patch_app(self.id, description=description,
            name=name, redirectUri=redirectUri)
        for k in res:
            setattr(self, k, res[k])
        return self

    def delete(self):
        """
        Deletes the app from the relayr platform.
        """
        res = self.api.delete_publisher(self.id)

    def register(self, name, publisher):
        """
        Adds the app to the relayr platform.

        :param name: the app name to be set
        :type name: string
        :param publisher: the publisher to be set
        :type publisher: string(?)
        """
        raise NotImplementedError


class Group(object):
    """
    A relayr device group.

    A device group is simply an ordered list of devices with its own ID,
    name and owner. The position of the group is the one where it appears
    when asking for the list of all groups. This position can be changed.
    """

    def __init__(self, id=None, client=None):
        """
        Instantiate new device group with given UUID and API client.

        :param id: the UUID of this group
        :type id: string
        :param client: the the user's UUID who is the owner of this group
        :type client: :py:class:`relayr.client.Client`
        :rtype: self
        """
        self.id = id
        self.devices = []
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def create(self, name, owner=None):
        """
        Create new device group with given name and owner.

        :param name: the name of this group
        :type name: string
        :param owner: the the user's UUID who is the owner of this group
        :type owner: string
        :rtype: self
        """

        if self.id is None:
            res = self.client.api.post_user_device_group(name, owner)
            self.id = res['id']
        return self

    def get_info(self):
        """
        Retrieves device group info and stores it as instance attributes.

        :rtype: self.
        """

        res = self.client.api.get_user_device_group(self.id)
        for k in res:
            if k == 'devices':
                for res2 in res[k]:
                    d = Device(res2['id'], client=self.client)
                    d.get_info()
                    # add position field used in a group context
                    if 'position' in res2:
                        d.position = res2['position']
                    self.devices.append(d)
            else:
                setattr(self, k, res[k])
        return self

    def update(self, name=None, position=None):
        """
        Updates position of this group in the list of all groups.

        :param name: the new name of this group
        :type name: string
        :param position: the new position of this group in the list of all groups
        :type position: integer
        :rtype: self
        """

        # returns None
        self.client.api.patch_user_device_group(self.id, name=name, position=position)
        return self

    def delete(self):
        """
        Deletes the group from the relayr platform.

        :rtype: self
        """

        res = self.client.api.delete_user_device_group(self.id)
        return self

    def add_device(self, device):
        """
        Add a device from the relayr platform to this device group.

        :param device: a relayr device object
        :type device: :py:class:`relayr.resources.Device`
        :rtype: self
        """

        res = self.client.api.post_user_device_group_device(self.id, device.id)
        return self

    def remove_device(self, device):
        """
        Remove a device from the relayr platform from this device group.

        :param device: a relayr device object
        :type device: :py:class:`relayr.resources.Device`
        :rtype: self
        """

        res = self.client.api.delete_user_device_group_device(self.id, device.id)
        return self

    def update_device(self, device, position=None):
        """
        Update a device inside this device group (now only the position field).

        :param device: a relayr device object
        :type device: :py:class:`relayr.resources.Device`
        :param position: the new position of the device in the list of all devices
        :type position: integer
        :rtype: self
        """

        res = self.client.api.patch_user_device_group_device(self.id, device.id, position)
        return self


class Device(object):
    """
    A relayr device.
    """

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self):
        """
        Retrieves device info and stores it as instance attributes.

        :rtype: self.
        """

        res = self.client.api.get_device(self.id)
        for k in res:
            if k == 'model':
                self.model = DeviceModel(res[k]['id'], client=self.client)
                self.model.get_info()
            else:
                setattr(self, k, res[k])
        return self

    def update(self, description=None, name=None, modelID=None, public=None):
        """
        Updates certain fields in the device information.
        
        :param description: the description to be set
        :type description: string
        :param name: the user name to be set
        :type name: string
        :param modelID: the device model to be set
        :type modelID: string?
        :param public: a Boolean flag for making the device public
        :type public: bool
        :rtype: self
        """

        res = self.client.api.patch_device(self.id, description=description,
            name=name, modelID=modelID, public=public)
        for k in res:
            setattr(self, k, res[k])
        return self

    def get_connected_apps(self):
        """
        Retrieves all apps connected to the device.
        
        :rtype: A list of apps.
        """
        for app_json in self.client.api.get_device_apps(self.id):
            app = App(id=app_json['id'], client=self.client)
            app.get_info()
            yield app

    def send_command(self, command):
        """
        Sends a command to the device.

        :param command: the command to be sent (containing three key strings:
            'path', 'command' and 'value')
        :type command: dict
        """
        
        res = self.client.api.post_device_command(self.id, command)
        return res

    def send_data(self, data):
        """
        Sends a data package to the device.

        :param data: the data to be sent
        :type data: dict
        """
        res = self.client.api.post_device_data(self.id, data)
        return res

    def send_config(self, data):
        """
        Sends a data package to configure the device.

        At the moment this can be only the frequency (in fact, the sampling
        period) for sending sensor data, so the only value for ``data``
        showing any effect is e.g. ``{'frequency': 500}`` (in milliseconds).

        :param data: the config data to be sent
        :type data: dict
        """
        res = self.client.api.post_device_configuration(self.id, **data)
        return res

    def delete(self):
        """
        Deletes the device from the relayr platform.

        :type command: self
        """
        
        res = self.client.api.delete_device(self.id)
        return self

    def switch_led_on(self, bool=True):
        """
        Switches on device's LED for ca. 10 seconds or switches it off.

        :param bool: the desired state, on if True (default), off if False
        :type bool: boolean
        :type command: self
        """
        data = {'path': 'led', 'command': 'cmd', 'value': int(bool)}
        res = self.client.api.post_device_command_led(self.id, data)
        return self

    def get_data(self, start=None, end=None, duration=None, meaning=None, sample=None, offset=None, limit=None):
        """
        Get a chunk of historical data recorded in the past for this device.

        Exactly one of the parameters ``start``, ``end`` and ``duration`` must
        be None, else an ``AssertionError`` is raised. The data will be returned
        using a paging mechanism with up to 10000 data points per page (``limit``).

        :param start: datetime value
        :type start: ISO 8601 string or ``datetime.datetime`` instance or milliseconds or None
        :param end: datetime value
        :type end: ISO 8601 string or ``datetime.datetime`` instance or milliseconds or None
        :param duration: time duration
        :type duration: ISO 8601 duration string or ``datetime.timedelta`` instance or milliseconds or None
        :rtype: a dict with historical data plus meta-information
        """
        start, end = get_start_end(start=start, end=end, duration=duration)
        start = datetime_to_millis(start)
        end = datetime_to_millis(end)
        res = self.client.api.get_history_devices(self.id,
            start=start, end=end, meaning=meaning, sample=sample, offset=offset, limit=limit)
        return res

    # new methods for transport channels

    def create_channel(self, transport):
        res = self.client.api.post_channel(self.id, transport)
        return res

    def delete_channel(self, channelID):
        res = self.client.api.delete_channel_id(channelID)
        return res

    def delete_channels(self):
        # should be rather on app or user...
        # api.delete_channels_device_transport(deviceID, transport)
        msg = 'This method should be rather in the class App or User...'
        raise NotImplementedError(msg)

    def list_channels(self):
        res = self.client.api.get_device_channels(self.id)
        return res


class DeviceModel(object):
    """
    relayr device model.
    """
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self):
        """
        Returns device model info and stores it as instance attributes.
        
        :rtype: self.
        """
        res = self.client.api.get_device_model(self.id)
        for k, v in res.items():
            setattr(self, k, v)
        return self


class Transmitter(object):
    "A relayr transmitter, The Master Module, for example."
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        args = (self.__class__.__name__, self.id)
        return "%s(id=%r)" % args

    def get_info(self):
        """
        Retrieves transmitter info.
        """
        res = self.client.api.get_transmitter(self.id)
        for k, v in res.items():
            setattr(self, k, v)
        return self

    def delete(self):
        """
        Deletes the transmitter from the relayr platform.

        :type command: self
        """
        
        res = self.client.api.delete_transmitter(self.id)
        return self

    def update(self, name=None):
        """
        Updates transmitter info.
        """
        res = self.client.api.patch_transmitter(self.id, name=name)
        for k, v in res.items():
            setattr(self, k, v)
        return self

    def get_connected_devices(self):
        """
        Returns a list of devices connected to the specific transmitter.
        
        :rtype: A list of devices.
        """
        res = self.client.api.get_transmitter_devices(self.id)
        for d in res:
            dev = Device(d['id'], client=self.client)
            dev.get_info()
            yield dev
