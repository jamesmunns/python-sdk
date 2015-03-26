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


def get_start_end(start=None, end=None, duration=None):
    """
    Get start and end datetime stamps in ISO 8601 format.

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

    # ensure we have exactly one None value
    assert [start, end, duration].count(None) == 1

    # convert iso datetime and duration values to datetime or timedelta
    if type(start) in (str, unicode):
        start = isodate.parse_datetime(start)
    if type(end) in (str, unicode):
        end = isodate.parse_datetime(end)
    if type(duration) in (str, unicode):
        duration = isodate.parse_duration(duration)

    # calculate missing start or end value using duration
    if end == None:
        end = start + duration
    elif start == None:
        start = end - duration

    # convert to iso
    start = isodate.datetime_isoformat(start)
    end = isodate.datetime_isoformat(end)

    return start, end


if __name__ == '__main__':
    dt = datetime.datetime.now()
    td = datetime.timedelta(days=1)
    print(get_start_end(start=dt, duration=td))
    