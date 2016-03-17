#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Misc. helpers...
"""

import datetime

import isodate

from relayr.compat import PY3


if PY3:
    unicode = str


epoch = datetime.datetime.utcfromtimestamp(0)


def datetime_to_millis(dt):
    "Convert given UTC datetime object to the integer number of miliseconds since the Unix epoch."

    return int((dt - epoch).total_seconds() * 1000.0)


def millis_to_datetime(millis):
    "Convert given number of miliseconds since the Unix epoch to a UTC datetime object."

    return datetime.datetime.utcfromtimestamp(millis / 1000.)


def get_start_end(start=None, end=None, duration=None):
    """
    Get start and end datetime objects from given input parameters.

    Input parameters are strings in ISO 8601.

    Exactly one of the parameters start, end and duration must be None, else
    an AssertionError is raised.

    See here more about `ISO 8601 durations <http://en.wikipedia.org/wiki/ISO_8601#Durations>`_.

    :param start: datetime value
    :type start: ISO 8601 string or ``datetime.datetime`` instance or None
    :param end: datetime value
    :type end: ISO 8601 string or ``datetime.datetime`` instance or None
    :param duration: time duration
    :type duration: ISO 8601 duration string or ``datetime.timedelta`` instance or None
    :rtype: tuple of two strings, both representing a datetime value in ISO 8601.
    """

    # ensure we have correct number of None values
    assert [start, end].count(None) <= 1
    if duration:
        assert [start, end].count(None) == 1

    # convert iso datetime and duration values to datetime or timedelta
    if type(start) in (str, unicode):
        start = isodate.parse_datetime(start)
    if type(end) in (str, unicode):
        end = isodate.parse_datetime(end)
    if type(duration) in (str, unicode):
        duration = isodate.parse_duration(duration)
        assert duration >= datetime.timedelta(0)

    # calculate missing start or end value using duration
    if duration:
        if end is None:
            end = start + duration
        elif start is None:
            start = end - duration

    if start and end is None and duration is None:
        end = datetime.datetime.utcnow()

    # swap start/end if needed
    if start > end:
        start, end = end, start

    # convert to iso
    # start = isodate.datetime_isoformat(start)
    # end = isodate.datetime_isoformat(end)

    return start, end


if __name__ == '__main__':
    dt = datetime.datetime.now()
    td = datetime.timedelta(days=1)
    print(get_start_end(start=dt, duration=td))
    print(get_start_end(end=dt, duration=td))
