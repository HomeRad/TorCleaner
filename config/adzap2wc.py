#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# this script has to be executed in the config parent dir
"""Generate WebCleaner .zap files from an AdZapper squid_redirect file"""

import sys
import os
import os.path
import re
import time
import tempfile
import urllib2
import urlparse
import errno
import wc
import wc.XmlUtils

DOWNLOAD = "downloads"
ADZAPPER_URL = "http://adzapper.sourceforge.net/scripts/squid_redirect"
ADZAPPER_FILE = "%s/squid_redirect" % DOWNLOAD

# used for .zap file timestamp
date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def download_adzapper_file ():
    """download adzapper url into temporary file and return filename"""
    fd, tmpfile = tempfile.mkstemp(".txt", "adzapper_", DOWNLOAD, text=True)
    f = os.fdopen(fd, "w")
    try:
        urldata = urllib2.urlopen(ADZAPPER_URL)
        f.write(urldata.read())
    finally:
        f.close()
    return tmpfile


def diff (file1, file2):
    """return True if file1 and file2 differ"""
    if not os.path.exists(file1):
        raise IOError, "%s not found" % `file1`
    if not os.path.exists(file2):
        return True
    scmd = 'diff %s %s' % (file1, file2)
    status = os.system(scmd)
    if status==0:
        return False
    if status!=1:
        raise IOError, "%s command failed" % scmd
    return True


# adapted from and copyrighted by Python distuilts.file_util.move
def move (src, dst):
    """move src to dst, possibly overwriting file2"""
    if not os.path.isfile(src):
        raise IOError, "can't move %s: not a regular file" % `src`

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    elif os.path.exists(dst):
        raise IOError, "can't move %s: destination %s already exists" % \
              (`src`, `dst`)

    if not os.path.isdir(os.path.dirname(dst)):
        raise IOError, "can't move %s: destination %s not a valid path" % \
              (`src`, `dst`)

    copy_it = 0
    try:
        os.rename(src, dst)
    except os.error, (num, msg):
        if num == errno.EXDEV:
            copy_it = 1
        else:
            raise IOError, "couldn't move %s to %s: %s" % (`src`, `dst`, msg)

    if copy_it:
        copy_file(src, dst)
        try:
            os.unlink(src)
        except os.error, (num, msg):
            try:
                os.unlink(dst)
            except os.error:
                pass
            raise IOError, ("couldn't move %s to %s by copy/delete: " +
                   "delete %s failed: %s") % \
                  (`src`, `dst`, `src`, msg)


def remove (filename):
    os.unlink(filename)


def parse_adzapper_file (filename):
    res = []
    is_comment = re.compile('^\s*(#.*)?$').match
    content = False # skip content until __DATA__ marker
    for i, line in enumerate(file(filename)):
        if not content:
            content = line.startswith('__DATA__')
        elif not is_comment(line):
            parse_adzapper_line(line.strip(), i+1, res)
    return res


def parse_adzapper_line (line, lineno, res):
    item = [lineno] + list(line.split(None, 1))
    res.append(item)


def write_filters (res, filename):
    if os.path.exists(filename):
        remove(filename)
    zapfile = file(filename, 'w')
    d = {
        "charset": wc.ConfigCharset,
        "title_en": wc.XmlUtils.xmlquote("AdZapper filters"),
        "title_de": wc.XmlUtils.xmlquote("AdZapper Filter"),
        "desc_en": wc.XmlUtils.xmlquote("Automatically generated by adzap2wc.py from %s on %s"%(ADZAPPER_URL, date)),
        "desc_de": wc.XmlUtils.xmlquote("Automatisch erzeugt von adzap2wc.py aus %s am %s"%(ADZAPPER_URL, date)),
    }
    zapfile.write("""<?xml version="1.0" encoding="%(charset)s"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder disable="0">
<title lang="en">%(title_en)s</title>
<title lang="de">%(title_de)s</title>
<description lang="en">%(desc_en)s</description>
<description lang="de">%(desc_de)s</description>
""" % d)
    for lineno, adclass, pattern in res:
        if adclass=='NOZAP':
            # no NOZAP stuff
            continue
        elif adclass=='PASS':
            write_allow(zapfile, adclass, pattern, lineno)
        elif adclass=='PRINT':
            pattern, replace = pattern.split(None, 1)
            write_block(zapfile, adclass, pattern, lineno, replace=replace)
        else:
            write_block(zapfile, adclass, pattern, lineno)
    zapfile.write("</folder>\n")
    zapfile.close()


def convert_adzapper_pattern (pattern):
    pattern = pattern.replace(".", "\\.")
    pattern = pattern.replace("?", "\\?")
    pattern = pattern.replace("+", "\\+")
    # this is overkill
    #pattern = re.sub(r"/(?!/)", r"/+", pattern)
    pattern = pattern.replace("**", ".*")
    pattern = re.sub(r"([^.])\*", r"\1[^/]*", pattern)
    return pattern


def convert_adzapper_replace (replace):
    # replace Perl back references with Python ones
    replace = re.sub(r"\${?(\d)}?", r"\\\1", replace)
    return replace


def write_allow (zapfile, adclass, pattern, lineno):
    #print "%s allow %s" % (adclass, `pattern`)
    d = get_rule_dict(adclass, pattern, lineno)
    zapfile.write("""<allow
 url="%(url)s"/>
  <title lang="en">%(title_en)s</title>
  <title lang="de">%(title_de)s</title>
  <description lang="en">%(desc_en)s</description>
  <description lang="de">%(desc_de)s</description>
""" % d)


def write_block (zapfile, adclass, pattern, lineno, replace=None):
    #print "%s block %s => %s" % (adclass, `pattern`, `replacement`)
    d = get_rule_dict(adclass, pattern, lineno, replace=replace)
    zapfile.write("""<block
 url="%(url)s""" % d)
    zapfile.write("\"")
    if adclass=='PRINT':
        zapfile.write("\n disable=\"1\">")
    zapfile.write("""
<title lang="en">%(title_en)s</title>
<title lang="de">%(title_de)s</title>
<description lang="en">%(desc_en)s</description>
<description lang="de">%(desc_de)s</description>
""" % d)
    if replace is not None:
        zapfile.write("  <replacement>%s</replacement>"%wc.XmlUtils.xmlquote(convert_adzapper_replace(replace)))
    zapfile.write("\n</block>")


def get_rule_dict (adclass, pattern, lineno, replace=None):
    d = {
        'title_en': wc.XmlUtils.xmlquote("%s filter line %d" % (adclass, lineno)),
        'title_de': wc.XmlUtils.xmlquote("%s Filter Zeile %d" % (adclass, lineno)),
        'desc_en': wc.XmlUtils.xmlquote("AdZapper pattern:\n%s." % pattern),
        'desc_de': wc.XmlUtils.xmlquote("AdZapper Pattern:\n%s." % pattern),
        'url': wc.XmlUtils.xmlquote(convert_adzapper_pattern(pattern)),
    }
    if replace is not None:
        d['desc_en'] += wc.XmlUtils.xmlquote("\nReplacement:\n%s." % replace)
        d['desc_de'] += wc.XmlUtils.xmlquote("\nErsatzwert:\n%s." % replace)
    return d


def _test ():
    ads = parse_adzapper_file(ADZAPPER_FILE)
    filename = os.path.join("config", "adzapper.zap")
    write_filters(ads, filename)


if __name__=='__main__':
    _test()
    #tmpfile = download_adzapper_file()
    #if diff(tmpfile, ADZAPPER_FILE):
    #    move(tmpfile, ADZAPPER_FILE)
    #    ads = parse_adzapper_file(tmpfile)
    #    filename = os.path.join("config", "adzapper.zap")
    #    if os.path.exists(filename):
    #        merge_filters(ads, filename)
    #    else:
    #        write_filters(ads, filename)
    #else:
    #    print "No changes in AdZapper config"
    #    remove(tmpfile)
