
def strtime (t):
    """return ISO 8601 formatted time"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + \
           strtimezone()


def strduration (duration):
    """return string formatted time duration"""
    name = i18n._("seconds")
    if duration > 60:
        duration = duration / 60
        name = i18n._("minutes")
    if duration > 60:
        duration = duration / 60
        name = i18n._("hours")
    return " %.3f %s"%(duration, name)


def strtimezone ():
    """return timezone info, %z on some platforms, but not supported on all"""
    if time.daylight:
        zone = time.altzone
    else:
        zone = time.timezone
    return "%+04d" % int(-zone/3600)

import time
from wc import i18n

