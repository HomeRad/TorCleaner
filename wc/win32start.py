# -*- coding: iso-8859-1 -*-
"""Windows specific helper functions.
   Needs Python with win32 extensions or Active Python installed.
"""
# Copyright (C) 2001-2004  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

try:
    import win32service
    import win32serviceutil
    import win32event
    service_klass = win32serviceutil.ServiceFramework
except ImportError:
    # assume non-windows platform
    service_klass = object
import wc
import wc.i18n


class ProxyService (service_klass):
    """NT service class for the WebCleaner proxy"""

    _svc_name_ = wc.AppName
    _svc_display_name_ = wc.i18n._("%s Proxy") % wc.AppName
    configdir = wc.ConfigDir
    filelogs = True

    def __init__ (self, args):
        """initialize service framework and set stop handler"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop (self):
        """stop this service"""
        # Before we do anything, tell the SCM we are starting the
        # stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun (self):
        """start this service"""
        import servicemanager
        # Log a "started" message to the event log.
        servicemanager.LogMsg(
           servicemanager.EVENTLOG_INFORMATION_TYPE,
           servicemanager.PYS_SERVICE_STARTED,
           (self._svc_name_, ''))
        wc.wstartfunc(handle=self.hWaitStop, confdir=self.configdir,
                      filelogs=self.filelogs)
        # Now log a "service stopped" message
        servicemanager.LogMsg(
           servicemanager.EVENTLOG_INFORMATION_TYPE,
           servicemanager.PYS_SERVICE_STOPPED,
           (self._svc_name_,''))


def _service_status (status):
    """convert status tuple information obtained from
       QueryServiceStatus into readable message and return it"""
    svcType, svcState, svcControls, err, svcErr, svcCP, svcWH = status
    msg = ""
    if svcType & win32service.SERVICE_WIN32_OWN_PROCESS:
        msg += "\n"+\
            wc.i18n._("The %s service runs in its own process.")%wc.AppName
    if svcType & win32service.SERVICE_WIN32_SHARE_PROCESS:
        msg += "\n"+\
 wc.i18n._("The %s service shares a process with other services.")%wc.AppName
    if svcType & win32service.SERVICE_INTERACTIVE_PROCESS:
        msg += "\n"+\
        wc.i18n._("The %s service can interact with the desktop.")%wc.AppName
    # Other svcType flags not shown.
    if svcState==win32service.SERVICE_STOPPED:
        msg += "\n"+wc.i18n._("The %s service is stopped.")%wc.AppName
    elif svcState==win32service.SERVICE_START_PENDING:
        msg += "\n"+wc.i18n._("The %s service is starting.")%wc.AppName
    elif svcState==win32service.SERVICE_STOP_PENDING:
        msg += "\n"+wc.i18n._("The %s service is stopping.")%wc.AppName
    elif svcState==win32service.SERVICE_RUNNING:
        msg += "\n"+wc.i18n._("The %s service is running.")%wc.AppName
    # Other svcState flags not shown.
    if svcControls & win32service.SERVICE_ACCEPT_STOP:
        msg += "\n"+wc.i18n._("The %s service can be stopped.")%wc.AppName
    if svcControls & win32service.SERVICE_ACCEPT_PAUSE_CONTINUE:
        msg += "\n"+wc.i18n._("The %s service can be paused.")%wc.AppName
    # Other svcControls flags not shown
    return msg.strip()


def status ():
    """return message with current status of WebCleaner service"""
    return _service_status(win32serviceutil.QueryServiceStatus(
                                                     wc.AppName))
