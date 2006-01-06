#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# this script has to be executed in the config parent dir
"""
Generate blacklist_XYZ folders with blocking and rewriting
filters for the given blacklist files.
The XYZ folder name is the blacklist folder.

Required are the "tarfile" module and Python 2.2
"""

import time
import os
import re
import urllib2
import gzip
import tarfile
import wc
import wc.configuration
import wc.XmlUtils

# global vars
date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
line_re = re.compile(r"^[0-9\^a-zA-Z_\-/\\+?#.;%()\[\]\~|$=]+$")
# <domain> --> <category> --> None
domains = {}
# <url> --> <category> --> None
urls = {}
# <expression> --> <category> --> None
expressions = {}
# <category> --> <type> --> <file>
categories = {}

# only accept these categories
mycats = ['ads', 'violence', 'aggressive']
transcats = {
    'ads': {'de': 'Werbung'},
    'violence': {'de': 'Gewalt'},
    'aggressive': {'de': 'Aggression'},
}

transtypes = {
    'blacklist': {'de': 'Filter für'},
    'whitelist': {'de': 'Erlaubnis für'},
}

# only extract these files
myfiles = ['domains', 'expressions', 'urls']
###################### read blacklist data #########################

def read_blacklists (fname):
    print "read", fname, "blacklists"
    if os.path.isdir(fname):
        for f in os.listdir(fname):
            read_blacklists(os.path.join(fname, f))
    else:
        if fname.endswith(".gz"):
            f = gzip.open(fname)
            fname = fname[:-3]
            w = file(fname, 'wb')
            w.write(f.read())
            w.close()
            f.close()
            os.remove(fname+".gz")
        if fname.endswith("domains"):
            read_data(fname, "domains", domains)
        elif fname.endswith("urls"):
            read_data(fname, "urls", urls)
        elif fname.endswith("expressions"):
            read_data(fname, "expressions", expressions)


def read_data (fname, name, data):
    cat = os.path.basename(os.path.dirname(fname))
    if cat not in mycats:
        return
    f = file(fname)
    line = f.readline()
    while line:
        line = line.strip()
        if line and line[0]!='#' and line_re.match(line):
            categories.setdefault(cat, {})[name] = None
            if name=="expressions":
                data.setdefault(cat, []).append(line)
            else:
                data.setdefault(line, {})[cat] = None
        line = f.readline()
    f.close()


def read_ids (filename, ids):
    p = wc.configuration.ZapperParser(filename)
    p.parse()
    ids['folder']['sid'] = str(p.folder.sid)
    ids['folder']['oid'] = p.folder.oid
    ids['folder']['configversion'] = str(p.folder.configversion)
    for rule in p.folder.rules:
        for ftype in ('domains', 'urls'):
            if rule.name.endswith(ftype):
                ids[ftype]['sid'] = str(rule.sid)


##################### write blacklist data ########################

def write_filters ():
    for cat, data in categories.items():
        if cat == 'kids_and_teens':
            ftype = 'whitelist'
        else:
            ftype = 'blacklist'
        filename = "config/%s_%s.zap" % (ftype, cat)
        print "writing", filename
        ids = {
            'folder': {'sid': None, 'oid': None, 'configversion': None},
            'domains': {'sid': None},
            'urls': {'sid': None},
        }
        if os.path.exists(filename):
            read_ids(filename, ids)
            os.remove(filename)
	f = file(filename, 'wb')
	write_folder(cat, ftype, data, ids, f)
        f.close()


def write_folder (cat, ftype, data, ids, f):
    print "write", cat, "folder"
    if ids['folder']['sid'] is not None:
        sid = ' sid="%s"' % ids['folder']['sid']
    else:
        sid = ""
    if ids['folder']['oid'] is not None:
        oid = ' oid="%d"' % ids['folder']['oid']
    else:
        oid = ""
    if ids['folder']['configversion'] is not None:
        configversion = ' configversion="%s"' % ids['folder']['configversion']
    else:
        configversion = ""
    d = {
        "charset": wc.configuration.ConfigCharset,
        "title_en": wc.XmlUtils.xmlquote("%s %s" %
                                     (ftype.capitalize(), cat)),
        "title_de": wc.XmlUtils.xmlquote("%s %s" %
                            (transtypes[ftype]['de'].capitalize(),
                             transcats[cat]['de'].capitalize())),
        "desc_en": wc.XmlUtils.xmlquote(
                                     "Automatically generated on %s" % date),
        "desc_de": wc.XmlUtils.xmlquote("Automatisch generiert am %s" % date),
        "sid": sid,
        "oid": oid,
        "configversion": configversion,
    }
    f.write("""<?xml version="1.0" encoding="%(charset)s"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder%(sid)s%(oid)s%(configversion)s>
<title lang="en">%(title_en)s</title>
<title lang="de">%(title_de)s</title>
<description lang="en">%(desc_en)s</description>
<description lang="de">%(desc_de)s</description>
""" % d)
    for t in data.keys():
        if cat == 'kids_and_teens':
            b = "whitelists"
            ftype = "allow"
        else:
            b = "blacklists"
            ftype = "block"
        globals()["write_%s" % t](cat, b, ftype, ids, f)
    f.write("</folder>\n")


def write_domains (cat, b, ftype, ids, f):
    print "write", cat, "domains"
    d = {
        'title_en': "%s domain filter"%cat.capitalize(),
        'title_de': "%s Rechnername Filter"%transcats[cat]['de'].capitalize(),
        'desc_en': """You should not edit this filter, only disable or delete it.
To update the filter data, run config/bl2wc.py from a WebCleaner source tree.""",
        'desc_de': """Sie sollten diesen Filter nicht editieren, nur deaktivieren oder löschen.
Um die Filterdaten zu aktualisieren, starten Sie config/bl2wc.py von einem WebCleaner Quellverzeichnis.""",
        'filename': "%s/%s/domains.gz" % (b, cat),
        'type': ftype,
        "sid": ids['domains']['sid'],
    }
    f.write("""<%(type)sdomains sid="%(sid)s"
 filename="%(filename)s">
  <title lang="en">%(title_en)s</title>
  <title lang="de">%(title_de)s</title>
  <description lang="en">%(desc_en)s</description>
  <description lang="de">%(desc_de)s</description>
""" % d)
    f.write("</%(type)sdomains>" % d)

def write_urls (cat, b, ftype, ids, f):
    print "write", cat, "urls"
    d = {
        'title_en': "%s url filter"%cat.capitalize(),
        'title_de': "%s URL Filter"%transcats[cat]['de'].capitalize(),
        'desc_en': """You should not edit this filter, only disable or delete it.
To update the filter data, run config/bl2wc.py from a WebCleaner source tree.""",
        'desc_de': """Sie sollten diesen Filter nicht editieren, nur deaktivieren oder löschen.
Um die Filterdaten zu aktualisieren, starten Sie config/bl2wc.py von einem WebCleaner Quellverzeichnis.""",
        'filename': "%s/%s/urls.gz" % (b, cat),
        'type': ftype,
        "sid": ids['urls']['sid'],
    }
    f.write("""<%(type)surls sid="%(sid)s"
 filename="%(filename)s">
  <title lang="en">%(title_en)s</title>
  <title lang="de">%(title_de)s</title>
  <description lang="en">%(desc_en)s</description>
  <description lang="de">%(desc_de)s</description>
""" % d)
    f.write("</%(type)surls>" % d)


def write_expressions (cat, b, ftype, f):
    d = {
        'title_en': "%s expression filter"%cat.capitalize(),
        'title_de': "%s Ausdruckfilter"%transcats[cat]['de'].capitalize(),
        'desc_en': """Automatically generated, you should not edit this filter.
To update the filter data, run config/bl2wc.py from a WebCleaner source tree.""",
        'desc_de': """Sie sollten diesen Filter nicht editieren, nur deaktivieren oder löschen.
Um die Filterdaten zu aktualisieren, starten Sie config/bl2wc.py von einem WebCleaner Quellverzeichnis.""",
        'type': ftype,
    }
    print "write", cat, "expressions"
    for expr in expressions[cat]:
        d['path'] = wc.XmlUtils.xmlquote(expr)
        f.write("""<%(type)s
 scheme=""
 host=""
 path="%(path)s"
 query=""
 fragment="">
  <title lang="en">%(title_en)s</title>
  <title lang="de">%(title_de)s</title>
  <description lang="en">%(desc_en)s</description>
  <description lang="de">%(desc_de)s</description>
""" % d)
    f.write("</%(type)s>" % d)


##################### other functions ############################

def blacklist (fname, extract_to="extracted"):
    source = os.path.join("downloads", fname)
    # extract tar
    if fname.endswith(".tar.gz") or fname.endswith(".tgz"):
        print "extracting archive", fname
        f = tarfile.TarFile.gzopen(source)
        for m in f:
            a, b = os.path.split(m.name)
            a = os.path.basename(a)
            if b in myfiles and a in mycats:
                print m.name
                f.extract(m, extract_to)
        f.close()
        read_blacklists(extract_to)
        rm_rf(extract_to)
    elif fname.endswith(".gz"):
        print "gunzip..."
        f = gzip.open(source)
        fname = "extracted/"+fname[:-3]
        os.makedirs(os.path.dirname(fname))
        w = file(fname, 'wb')
        w.write(f.read())
        w.close()
        f.close()
        read_data(fname, "domains", domains)


# for now, only kids_and_teens
def dmozlists (fname):
    print "filtering %s..." % fname
    smallfname = "small_%s"%fname
    if not os.path.exists("downloads/%s"%smallfname):
        os.system(("zcat downloads/%s | config/dmozfilter.py | "+ \
                  "gzip --best > downloads/%s") % (fname, smallfname))
    fname = smallfname
    print "dmozlist %s..." % fname
    f = gzip.GzipFile(os.path.join("downloads",fname))
    line = f.readline()
    topic = None
    while line:
        line = line.strip()
        if line.startswith("<Topic r:id="):
            topic = line[13:line.rindex('"')].split("/", 2)[1].lower()
        elif topic=='kids_and_teens' and line.startswith("<link r:resource="):
            #split url, and add to domains or urls
            url = line[18:line.rindex('"')]
            if url.startswith("http://"):
                url = url[7:]
                tup = url.split("/", 1)
                if len(tup)>1 and tup[1]:
                    categories.setdefault(topic, {})["urls"] = None
                    entry = "%s/%s" % (tup[0].lower(), tup[1])
                    urls.setdefault(entry, {})[topic] = None
                else:
                    categories.setdefault(topic, {})["domains"] = None
                    domains.setdefault(tup[0].lower(), {})[topic] = None
        line = f.readline()
    f.close()


def geturl (basedir, fname, fun, saveas=None):
    if saveas is not None:
        target = saveas
    else:
        target = fname
    if os.path.exists(os.path.join("downloads", target)):
        print "downloads/%s already exists" % target
    else:
        print "downloading", basedir+fname
        d = os.path.dirname(os.path.join("downloads", target))
        if not os.path.isdir(d):
            os.makedirs(d)
        try:
            urldata = urllib2.urlopen(basedir+fname)
            f = file(os.path.join("downloads", target), 'w')
            f.write(urldata.read())
            f.close()
        except urllib2.HTTPError, msg:
            print msg
            return
    fun(target)


def rm_rf (directory):
    for f in os.listdir(directory):
        f = os.path.join(directory, f)
        if os.path.isdir(f):
            rm_rf(f)
            if os.path.islink(f):
                os.remove(f)
            else:
                os.rmdir(f)
        else:
            os.remove(f)


def download_and_merge ():
    """Download all available filters and merge them"""
    # remove old files
    if not os.path.isdir("downloads"):
        os.mkdir("downloads")
    # from Pål Baltzersen and Lars Erik Håland (Squidguard guys)
    geturl("ftp://ftp.teledanmark.no/pub/www/proxy/squidGuard/contrib/", "blacklists.tar.gz", blacklist)
    # from Stefan Furtmayr
    geturl("http://www.bn-paf.de/filter/", "de-blacklists.tar.gz", blacklist)
    # from Craig Baird
    geturl("http://www.xpressweb.com/sg/", "sites.domains.gz", blacklist, saveas="porn/domains.gz")
    # from ?????
    geturl("http://squidguard.mesd.k12.or.us/", "blacklists.tgz", blacklist)
    # from fabrice Prigent
    geturl("ftp://ftp.univ-tlse1.fr/pub/reseau/cache/squidguard_contrib/", "blacklists.tar.gz", blacklist, saveas="contrib-blacklists.tar.gz")
    # dmoz category dumps
    # Note: the dmoz content license is not GPL compatible, so you may not
    # distribute it with WebCleaner!
    #geturl("http://dmoz.org/rdf/", "content.rdf.u8.gz", dmozlists)


def write_lists ():
    open_files("config")
    for data, name in ((domains,"domains"),(urls,"urls")):
        print "writing", name
        for key,val in data.items():
            if key=="thesimpsons.com":
                continue
            for cat in val.keys():
                categories[cat][name].write(key+"\n")
    close_files()


def open_files (directory):
    for cat in categories.keys():
        if cat=='kids_and_teens':
            d='whitelists'
        else:
            d='blacklists'
        basedir = os.path.join(directory, d, cat)
        if not os.path.isdir(basedir):
            os.makedirs(basedir)
        for ftype in categories[cat].keys():
            if ftype=="expressions": continue
            fname = os.path.join(basedir, "%s.gz" % ftype)
            if os.path.exists(fname):
                os.remove(fname)
            print "opening", fname
            categories[cat][ftype] = gzip.GzipFile(fname, 'wb')


def close_files ():
    for cat in categories.keys():
        for ftype in categories[cat].keys():
            f = categories[cat][ftype]
            if f is not None:
                print "closing", f.filename
                f.close()


def remove_old_data ():
    print "remove old extracted data..."
    for d in ("extracted", "config/blacklists_new"):
        if os.path.isdir(d):
            rm_rf(d)


def remove_gunziped_files (fname):
    if os.path.isdir(fname):
        for f in os.listdir(fname):
            remove_gunziped_files(fname+"/"+f)
    elif os.path.basename(fname) in ("domains", "urls", "expressions"):
        os.remove(fname)


if __name__=='__main__':
    remove_old_data()
    download_and_merge()
    write_lists()
    write_filters()
