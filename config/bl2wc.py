#!/usr/bin/python
"""convert a squidguard blacklist file into a webcleaner filter
It generates squidguard_XXX folders with blocking and rewriting
filters for the given blacklist files.
The XXX folder name is the blacklist folder.
"""

import sys, time, os, re, urlparse
from wc import xmlify

date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def usage ():
    print sys.argv[0], "<url-or-domain-file>..."
    sys.exit(0)


line_re = re.compile(r"^[0-9a-zA-Z_\-/\\+?#.;%()\[\]\~]+$")
def read_data (filename):
    return {"name": os.path.basename(os.path.dirname(filename)),
            "type": os.path.basename(filename),
           }


def gen_filter (data, folders):
    name = data["name"]
    if not folders.has_key(name):
        folders[name] = {"title": xmlify("SquidGuard "+name),
	                 "desc": xmlify("Automatically generated from "
                                        "SquidGuard blacklists "
                                        "on %s" % date),
                         'files': []
                        }
    folders[name]['files'].append(data['type'])


def print_filter (folders):
    for key, val in folders.items():
        filename = os.path.join("config", "squidguard_"+key+".zap")
        print "file", filename
        if os.path.exists(filename):
            if os.path.exists(filename+".old"):
                os.remove(filename+".old")
            os.rename(filename, filename+".old")
	file = open(filename, 'w')
	print_folder(key, val, file)
        file.close()


def print_folder (name, data, file):
    file.write("""<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="%(title)s"
 desc="%(desc)s"
 disable="1">
""" % data)
    for type in data['files']:
        globals()["print_%s"%type](name, file)
    file.write("</folder>")


def print_domains (name, file):
    d = {'title': name+" domain filter",
         'desc': "You should not edit this filter, only disable or delete it.",
         'file': "blacklists/"+name+"/domains.gz",
        }
    file.write("""<blockdomains
 title="%(title)s"
 desc="%(desc)s"
 file="%(file)s"/>
""" % d)


def print_urls (name, file):
    d = {'title': name+" url filter",
         'desc': "You should not edit this filter, only disable or delete it.",
         'file': "blacklists/"+name+"/urls.gz",
        }
    file.write("""<blockurls
 title="%(title)s"
 desc="%(desc)s"
 file="%(file)s"/>
""" % d)


def print_expressions (name, file):
    exprs = open("config/blacklists/%s/expressions"%name).readlines()
    for line in exprs:
        line = line.strip()
        if not line or line[0]=='#': continue
        print_expression(name, file, line)


def print_expression (name, file, expr):
    d = {'title': name+" expression filter",
         'desc': "Automatically generated, you should not edit this filter.",
         'path': xmlify(expr),
        }
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

if __name__=='__main__':
    folders = {}
    for arg in sys.argv[1:]:
        data = read_data(arg)
        gen_filter(data, folders)
    print_filter(folders)
