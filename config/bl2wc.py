#!/usr/bin/python2.2
# this script has to be executed in the config parent dir
"""Generate blacklist_XXX folders with blocking and rewriting
filters for the given blacklist files.
The XXX folder name is the blacklist folder.

Required are the "tarfile" module and Python 2.2
"""

import sys, time, os, re, urllib2, tarfile, gzip
sys.path.insert(0, os.getcwd())
from wc import xmlify

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
# only extract these files
myfiles = ['domains', 'expressions', 'urls']
###################### read blacklist data #########################

def read_blacklists (file):
    if os.path.isdir(file):
        for f in os.listdir(file):
            read_blacklists(file+"/"+f)
    else:
        if file.endswith(".gz"):
            f = gzip.open(file)
            file = file[:-3]
            w = open(file, 'wb')
            w.write(f.read())
            w.close()
            f.close()
            os.remove(file+".gz")
        if file.endswith("domains"):
            read_data(file, "domains", domains)
        elif file.endswith("urls"):
            read_data(file, "urls", urls)
        elif file.endswith("expressions"):
            read_data(file, "expressions", expressions)

def read_data (file, name, data):
    cat = os.path.basename(os.path.dirname(file))
    if cat not in mycats: return
    f = open(file)
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


##################### write blacklist data ########################

def write_filters (basedir):
    for cat, data in categories.items():
        if cat=='kids_and_teens':
            d = 'whitelist'
        else:
            d = 'blacklist'
        filename = os.path.join(basedir, "%s_%s.zap"%(d, cat))
        print "writing", filename
        if os.path.exists(filename):
            os.remove(filename)
	file = open(filename, 'wb')
	write_folder(cat, data, file)
        file.close()

def write_folder (cat, data, file):
    print "write", cat, "folder"
    d = {"title": xmlify("Blacklist "+cat),
         "desc": xmlify("Automatically generated from "
                        "several blacklists on %s" % date),
    }
    file.write("""<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="%(title)s"
 desc="%(desc)s"
 disable="0">
""" % d)
    for type in data.keys():
        globals()["write_%s"%type](cat, file)
    file.write("</folder>")

def write_domains (cat, file):
    print "write", cat, "domains"
    d = {'title': cat+" domain filter",
         'desc': "You should not edit this filter, only disable or delete it.",
         'file': "blacklists/"+cat+"/domains.gz",
        }
    file.write("""<blockdomains
 title="%(title)s"
 desc="%(desc)s"
 file="%(file)s"/>
""" % d)

def write_urls (cat, file):
    print "write", cat, "urls"
    d = {'title': cat+" url filter",
         'desc': "You should not edit this filter, only disable or delete it.",
         'file': "blacklists/"+cat+"/urls.gz",
        }
    file.write("""<blockurls
 title="%(title)s"
 desc="%(desc)s"
 file="%(file)s"/>
""" % d)

def write_expressions (cat, file):
    d = {'title': cat+" expression filter",
         'desc': "Automatically generated, you should not edit this filter.",
        }
    print "write", cat, "expressions"
    for expr in expressions[cat]:
        d['path'] = xmlify(expr)
        file.write("""<block
 title="%(title)s"
 desc="%(desc)s"
 scheme=""
 host=""
 path="%(path)s"
 parameters=""
 query=""
 fragment=""/>
""" % d)


##################### other functions ############################

def blacklist (file):
    source = "downloads/"+file
    # extract tar
    if file.endswith(".tar.gz"):
        print "extracting archive..."
        d = "extracted/"+file[:-7]
        f = tarfile.gzopen(source)
        for m in f:
            d, b = os.path.split(m.name)
            d = os.path.basename(d)
            if b in myfiles and d in mycats:
                print m.name
                f.extract(m, d)
        f.close()
        read_blacklists(d)
    elif file.endswith(".gz"):
        print "gunzip..."
        f = gzip.open(source)
        file = "extracted/"+file[:-3]
        os.makedirs(os.path.dirname(file))
        w = open(file, 'wb')
        w.write(f.read())
        w.close()
        f.close()
        read_data(file, "domains", domains)

# for now, only adult (later: kids_and_teens?)
def dmozlists (file):
    print "dmozlist %s..." % file
    f = gzip.GzipFile("downloads/"+file)
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

def geturl (basedir, file, fun, saveas=None):
    if saveas is not None:
        target = saveas
    else:
        target = file
    if os.path.exists("downloads/"+target):
        print "downloads/%s already exists"%target
    else:
        print "downloading", basedir+file
        d = os.path.dirname("downloads/"+target)
        if not os.path.isdir(d):
            os.makedirs(d)
        urldata = urllib2.urlopen(basedir+file)
        f = open("downloads/"+target, 'w')
        f.write(urldata.read())
        f.close()
    fun(target)

def rm_rf (directory):
    for f in os.listdir(directory):
        f = directory+"/"+f
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
    geturl("http://squidguard.mesd.k12.or.us/", "squidguard.tar.gz", blacklist)
    # from fabrice Prigent
    geturl("ftp://ftp.univ-tlse1.fr/pub/reseau/cache/squidguard_contrib/", "blacklists.tar.gz", blacklist, saveas="contrib-blacklists.tar.gz")
    # dmoz category dumps (this big fucker is 195MB !!!)
    geturl("http://dmoz.org/rdf/", "content.rdf.u8.gz", dmozlists, saveas="content.rdf.stripped.gz")

def write_blacklists (directory):
    open_files(directory)
    for data, name in ((domains,"domains"),(urls,"urls")):
        print "writing", name
        for key,val in data.items():
            for cat in val.keys():
                categories[cat][name].write(key+"\n")
    close_files()

def open_files (directory):
    for cat in categories.keys():
        if cat=='kids_and_teens':
            d='whitelists'
        else:
            d='blacklists'
        basedir = "%s/%s/%s" % (directory, d, cat)
        if not os.path.isdir(basedir):
            os.makedirs(basedir)
        for type in categories[cat].keys():
            if type=="expressions": continue
            file = "%s/%s.gz" % (basedir, type)
            if os.path.exists(file):
                os.remove(file)
            print "opening", file
            categories[cat][type] = gzip.GzipFile(file, 'wb')

def close_files ():
    for cat in categories.keys():
        for type in categories[cat].keys():
            f = categories[cat][type]
            if f is not None:
                print "closing", f.filename
                f.close()

def remove_old_data ():
    print "remove old extracted data..."
    for d in ("extracted", "config/blacklists_new"):
        if os.path.isdir(d):
            rm_rf(d)

def remove_gunziped_files (file):
    if os.path.isdir(file):
        for f in os.listdir(file):
            remove_gunziped_files(file+"/"+f)
    elif os.path.basename(file) in ("domains", "urls", "expressions"):
        os.remove(file)

if __name__=='__main__':
    remove_old_data()
    #print "read data..."
    #read_blacklists("config/blacklists")
    download_and_merge()
    write_blacklists("config")
    write_filters("config")
    #print "remove gunziped files"
    #remove_gunziped_files("config/blacklists")
