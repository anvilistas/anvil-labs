# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import datetime
import time


class tzoffset(datetime.tzinfo):
    def __init__(self, **kwargs):
        self._offset = datetime.timedelta(**kwargs)

    def utcoffset(self, dt):
        return self._offset

    def dst(self, dt):
        return datetime.timedelta()

    def tzname(self, dt):
        return None


class tzlocal(tzoffset):
    def __init__(self):
        if time.localtime().tm_isdst and time.daylight:
            s = -time.altzone
        else:
            s = -time.timezone
        tzoffset.__init__(self, seconds=s)


class tzutc(tzoffset):
    pass


UTC = tzutc()
