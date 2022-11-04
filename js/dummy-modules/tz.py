# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import datetime
import time


class tzoffset(datetime.tzinfo):
    def __init__(self, **kwargs):
        if (
            len(kwargs) > 1
            or len(kwargs) == 1
            and "seconds" not in kwargs
            and "hours" not in kwargs
            and "minutes" not in kwargs
        ):
            raise TypeError("bad initialization")
        self._offset = datetime.timedelta(**kwargs)

    def utcoffset(self, dt):
        return self._offset

    def dst(self, dt):
        return datetime.timedelta()

    def tzname(self, dt):
        return None

    def __repr__(self):
        return "tzoffset(%s hours)" % (self._offset.total_seconds() / 3600)


class tzlocal(tzoffset):
    def __init__(self):
        if time.localtime().tm_isdst and time.daylight:
            s = -time.altzone
        else:
            s = -time.timezone
        tzoffset.__init__(self, seconds=s)

    def __repr__(self):
        return "tzlocal(%s hour offset)" % (self._offset.total_seconds() / 3600)


class tzutc(tzoffset):
    def __init__(self):
        tzoffset.__init__(self, minutes=0)

    def __repr__(self):
        return "tzutc"


UTC = tzutc()
