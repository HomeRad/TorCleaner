# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010 Bastian Kleineidam
"""
Mail utils.
"""

import socket
import smtplib
import email.Utils
from . import log, LOG_GUI


def valid_mail(address):
    """Return cleaned up mail, or an empty string on errors."""
    cleaned = email.Utils.parseaddr(address)
    if not cleaned[0]:
        return cleaned[1]
    return '%s <%s>' % cleaned


def send_mail(smtphost, fromaddr, toaddrs, message):
    """Send mail, return False on error, else True."""
    try:
        conn = smtplib.SMTP(smtphost)
        conn.sendmail(fromaddr, toaddrs, message)
        conn.quit()
        return True
    except (socket.error, smtplib.SMTPException), x:
        log.exception(LOG_GUI, 'SMTP send failure: %s', x)
    return False


def mail_date():
    """Return date string formatted for a mail header."""
    return email.Utils.formatdate()
