# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
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
Search data stream for virus signatures.
"""
import socket
import sys
from .. import log, LOG_FILTER, fileutil
from . import Filter, STAGE_RESPONSE_MODIFY
from ..clamav import get_clamav_conf, ClamdScanner


class VirusFilter (Filter.Filter):
    """
    Scan for virus signatures in a data stream.
    """

    enable = True

    # 5 MB maximum file size, everything bigger will generate a proxy error
    MAX_FILE_BYTES = 1024L*1024L*5L

    def __init__ (self):
        """
        Init antivirus stages and mimes, read clamav config.
        """
        stages = [STAGE_RESPONSE_MODIFY]
        rulenames = ['antivirus']
        super(VirusFilter, self).__init__(stages=stages, rulenames=rulenames)
        if get_clamav_conf() is None:
            log.warn(LOG_FILTER, "Virus filter is enabled but " \
                        "not configured. Set the clamav configuration file.")

    def filter (self, data, attrs):
        """
        Write data to scanner and internal buffer.
        """
        if 'virus_buf' not in attrs:
            return data
        return attrs['virus_buf'].filter(data)

    def finish (self, data, attrs):
        """
        Write data to scanner and internal buffer.
        If scanner is clean, return buffered data, else print error
        message and return an empty string.
        """
        if 'virus_buf' not in attrs:
            return data
        return attrs['virus_buf'].finish(data)

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        Return virus scanner and internal data buffer.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(VirusFilter, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        if not rules:
            return
        conf = get_clamav_conf()
        if conf is not None:
            attrs['virus_buf'] = Buf(conf, url)


# 200kB chunk size, 50kB overlap
CHUNK_SIZE = 1024L*200L
CHUNK_OVERLAP = 1024L*50L

class Buf (fileutil.Buffer):
    """
    Holds buffer data ready for replacing, with overlapping scans.
    Strings must be unicode.
    """

    def __init__ (self, conf, url):
        """
        Store rules and initialize buffer.
        """
        super(Buf, self).__init__()
        self.conf = conf
        self.url = url

    def filter (self, data):
        """
        Fill up buffer with given data, and scan for replacements.
        """
        self.write(data)
        if len(self) > CHUNK_SIZE:
            return self.scan(self.flush(overlap=CHUNK_OVERLAP))
        return ""

    def finish (self, data):
        self.write(data)
        return self.scan(self.flush())

    def scan (self, data):
        """
        Scan for virus
        """
        scanner = ClamdScanner(self.conf)
        try:
            scanner.scan(data)
        except socket.error:
            msg = sys.exc_info()[1]
            log.warn(LOG_FILTER, "Virus scanner error %r", msg)
        scanner.close()
        for msg in scanner.errors:
            log.warn(LOG_FILTER, "Virus scanner error %r", msg)
        if scanner.infected:
            # XXX
            data = ""
            for msg in scanner.infected:
                log.warn(LOG_FILTER, "Found virus %r in %r",
                            msg, self.url)
        return data
