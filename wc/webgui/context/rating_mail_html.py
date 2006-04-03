# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
Parameters for rating_mail.html page.
"""

from wc import AppName, Email, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval
from wc.url import is_safe_url as _is_safe_url
from wc.mail import valid_mail as _valid_mail
from wc.mail import send_mail as _send_mail
from wc.mail import mail_date as _mail_date
from wc.rating.storage import get_rating_store as _get_rating_store
from wc.rating.storage.pickle import PickleStorage as _PickleStorage

info = {
    'send': False,
}
error = {
    'url': False,
    'rating': False,
    'smtphost': False,
    'fromaddr': False,
    'send': False,
}
url = ""
rating = None
smtphost = "localhost"
rating_store = _get_rating_store(_PickleStorage)

def _exec_form (form, lang):
    """
    HTML CGI form handling.
    """
    # calculate global vars
    if not _form_url(form):
        return
    if not _get_rating():
        return
    if form.has_key('send'):
        if not _form_send(form):
            return


def _form_reset ():
    """
    Reset form values.
    """
    for key in info.keys():
        info[key] = False
    for key in error.keys():
        error[key] = False
    global url, rating
    url = ""
    rating = None


def _form_url (form):
    """
    Set rating URL.
    """
    global url, rating
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_safe_url(val):
            error['url'] = True
            return False
        url = val
    return True


def _get_rating ():
    """
    Select a rating.
    """
    if not url:
        error["url"] = True
        return False
    if url not in rating_store:
        error["rating"] = True
        return False
    global rating
    rating = rating_store[url]
    return True


def _form_send (form):
    """
    Email a rating.
    """
    if not form.has_key('smtphost'):
        error['smtphost'] = True
        return False
    global smtphost
    smtphost = _getval(form, 'smtphost')
    if form.has_key('fromaddr'):
        fromaddr = _getval(form, 'fromaddr')
    else:
        fromaddr = "Wummel <%s>" % Email
    fromaddr = _valid_mail(fromaddr)
    if not fromaddr:
        error['fromaddr'] = True
        return False
    toaddrs = [Email]
    headers = []
    headers.append("From: %s" % fromaddr)
    headers.append("To: %s" % ", ".join(toaddrs))
    headers.append("Date: %s" % _mail_date())
    headers.append("Subject: Webcleaner rating for %s" % url)
    headers.append("X-WebCleaner: rating")
    message = "%s\r\n%s" % ("\r\n".join(headers), rating.serialize())
    if not _send_mail(smtphost, fromaddr, toaddrs, message):
        error['send'] = True
        return False
    info["send"] = True
    return True
