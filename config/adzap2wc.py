#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
# this script has to be executed in the config parent dir
"""Generate WebCleaner .zap files from an AdZapper squid_redirect file"""

import sys, os, re, time, urlparse
try:
    from wc.XmlUtils import xmlify
except ImportError:
    sys.path.insert(0, os.getcwd())
    from wc.XmlUtils import xmlify

DOWNLOAD = "downloads"
ADZAPPER_URL = "http://adzapper.sourceforge.net/scripts/squid_redirect"
ADZAPPER_FILE = "%s/squid_redirect" % DOWNLOAD

# used for .zap file timestamp
date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def download_adzapper_file ():
    """download adzapper url into temporary file and return filename"""
    import tempfile, urllib2
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
    from os.path import exists, isfile, isdir, basename, dirname
    import errno

    if not isfile(src):
        raise IOError, "can't move %s: not a regular file" % `src`

    if isdir(dst):
        dst = os.path.join(dst, basename(src))
    elif exists(dst):
        raise IOError, "can't move %s: destination %s already exists" % \
              (`src`, `dst`)

    if not isdir(dirname(dst)):
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
    for line in open(filename):
        if not content:
            content = line.startswith('__DATA__')
        elif not is_comment(line):
            parse_adzapper_line(line.strip(), res)
    return res


def parse_adzapper_line (line, res):
    res.append(line.split(None, 1))


def write_filters (res):
    filename = os.path.join("config", "adzapper.zap")
    if os.path.exists(filename):
        remove(filename)
    zapfile = file(filename, 'w')
    d = {"title": xmlify("AdZapper filters"),
         "desc": xmlify("Automatically generated on %s" % date),
    }
    zapfile.write("""<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="%(title)s"
 desc="%(desc)s"
 disable="0">
""" % d)
    for adclass, pattern in res:
        if adclass=='NOZAP':
            # no NOZAP stuff
            continue
        elif adclass=='PASS':
            pattern = convert_adzapper_pattern(pattern)
            write_allow(zapfile, adclass, pattern)
        elif adclass=='PRINT':
            pattern, replace = pattern.split(None, 1)
            pattern = convert_adzapper_pattern(pattern)
            replace = convert_adzapper_replace(replace)
            write_block(zapfile, adclass, pattern, replace)
        else:
            pattern = convert_adzapper_pattern(pattern)
            write_block(zapfile, adclass, pattern)
    zapfile.write("</folder>\n")
    zapfile.close()


def convert_adzapper_pattern (pattern):
    pattern = pattern.replace(".", "\\.")
    pattern = pattern.replace("?", "\\?")
    pattern = pattern.replace("+", "\\+")
    pattern = re.sub(r"/(?!/)", r"/+", pattern)
    pattern = pattern.replace("**", ".*?")
    pattern = re.sub(r"([^.])\*([^?]|$)", r"\1[^/]*\2", pattern)
    return pattern


def convert_adzapper_replace (replace):
    # replace Perl back references with Python ones
    replace = re.sub(r"\${?(\d)}?", r"\\\1", replace)
    return replace


def write_allow (zapfile, adclass, pattern):
    #print "%s allow %s" % (adclass, `pattern`)
    d = get_rule_dict(adclass, pattern)
    zapfile.write("""<allow
 title="%(title)s"
 desc="%(desc)s"
 url="%(url)s"/>
""" % d)


def write_block (zapfile, adclass, pattern, replacement=None):
    #print "%s block %s => %s" % (adclass, `pattern`, `replacement`)
    d = get_rule_dict(adclass, pattern)
    zapfile.write("""<block
 title="%(title)s"
 desc="%(desc)s"
 url="%(url)s""" % d)
    if replacement is not None:
        zapfile.write("\">%s</block>" % xmlify(replacement))
    else:
        zapfile.write("\"/>")
    zapfile.write("\n")


def get_rule_dict (adclass, pattern):
    return {
        'title': xmlify("AdZapper %s filter" % adclass),
        'desc': xmlify("Automatically generated, you should not edit this filter."),
        'url': xmlify(pattern),
    }


def download_and_parse ():
    tmpfile = download_adzapper_file()
    if diff(tmpfile, ADZAPPER_FILE):
        move(tmpfile, ADZAPPER_FILE)
        parse()
    else:
        print "No changes in AdZapper config"
        remove(tmpfile)


def parse ():
    ads = parse_adzapper_file(ADZAPPER_FILE)
    write_filters(ads)


if __name__=='__main__':
    #download_and_parse()
    parse()
