# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010 Bastian Kleineidam
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
"""
Mail utils.
"""

import socket
import smtplib
import email.Utils
from . import log, LOG_GUI


def valid_mail (address):
    """Return cleaned up mail, or an empty string on errors."""
    cleaned = email.Utils.parseaddr(address)
    if not cleaned[0]:
        return cleaned[1]
    return '%s <%s>' % cleaned


def send_mail (smtphost, fromaddr, toaddrs, message):
    """Send mail, return False on error, else True."""
    try:
        conn = smtplib.SMTP(smtphost)
        conn.sendmail(fromaddr, toaddrs, message)
        conn.quit()
        return True
    except (socket.error, smtplib.SMTPException), x:
        log.exception(LOG_GUI, 'SMTP send failure: %s', x)
    return False


def mail_date ():
    """Return date string formatted for a mail header."""
    return email.Utils.formatdate()
