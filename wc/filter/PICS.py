"""Parse and filter PICS data.
See http://www.w3.org/PICS/labels.html for more info.

The following rating standard associations are supported
(Servicematch is used to identify a service in a PICS label):

Name: Internet Content Rating Association (ICRA)
Url: http://www.icra.org/ratingsv02.html
Servicematch: icra

Name: Recreational Software Advisory Council (RSAC)
Url: http://www.rsac.org/ratingsv01.html
Servicematch: rsac

Name: Safesurf
Url: http://www.classify.org/safesurf/
Servicematch: safesurv

Name: Safe For Kids
Url: http://www.weburbia.com/safe/ratings.htm
Servicematch: weburbia

Name: EvaluWeb
Url: http://www.sserv.com/evaluweb/pics.html
Servicematch: evaluweb

Name: CyberNOT list (from CyberPatrol)
Url: http://www.microsys.com/support/top_questions.aspx#8
     http://pics.microsys.com (??? not viewable)
Servicematch: microsys

Name: Vancouver Web Pages
Url: http://vancouver-webpages.com/VWP1.0/
Servicematch: vancouver
"""
# Copyright (C) 2003  Bastian Kleineidam
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
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

if __name__=='__main__':
    import sys, os
    sys.path.insert(0, os.getcwd())
import re
from wc.log import *
from wc import i18n

# rating phrase searcher
ratings = re.compile(r'r(atings)?\s*\((?P<rating>[^)]*)\)').finditer

# PICS rating associations and their categories
services = {
  "safesurf": {'name': 'Safesurf',
               'categories': {'agerange':                '000',
                              'profanity':               '001',
                              'heterosexualthemes':      '002',
                              'homosexualthemes':        '003',
                              'nudity':                  '004',
                              'violence':                '005',
                              'sexviolenceandprofanity': '006',
                              'intolerance':             '007',
                              'druguse':                 '008',
                              'otheradultthemes':        '009',
                              'gambling':                '00A',
                             },
              },
  "evaluweb": {'name': 'evaluWEB',
               'categories': {'agerange': 'rating',
                             },
              },
  "microsys": {'name': 'CyberNOT',
               'categories': {'sexrating':   'sex',
                              'otherrating': 'other',
                             },
              },
  "icra":     {'name': 'ICRA',
               'categories': {'language':                   'la',
                              'chat':                       'ca',
                              'moderatedchat':              'cb',
                              'languageprofanity':          'lb',
                              'languagemildexpletives':     'lc',
                              'nuditygraphic':              'na',
                              'nuditymalegraphic':          'nb',
                              'nudityfemalegraphic':        'nc',
                              'nuditytopless':              'nd',
                              'nuditybottoms':              'ne',
                              'nuditysexualacts':           'nf',
                              'nudityobscuredsexualacts':   'ng',
                              'nuditysexualtouching':       'nh',
                              'nuditykissing':              'ni',
                              'nudityartistic':             'nr',
                              'nudityeducational':          'ns',
                              'nuditymedical':              'nt',
                              'drugstobacco':               'oa',
                              'drugsalcohol':               'ob',
                              'drugsuse':                   'oc',
                              'gambling':                   'od',
                              'weaponuse':                  'oe',
                              'intolerance':                'of',
                              'badexample':                 'og',
                              'pgmaterial':                 'oh',
                              'violencerape':               'va',
                              'violencetohumans':           'vb',
                              'violencetoanimals':          'vc',
                              'violencetofantasy':          'vd',
                              'violencekillinghumans':      've',
                              'violencekillinganimals':     'vf',
                              'violencekillingfantasy':     'vg',
                              'violencejuryhumans':         'vh',
                              'violencejuryanimals':        'vi',
                              'violencejuryfantasy':        'vj',
                              'violenceartistic':           'vr',
                              'violenceeducational':        'vs',
                              'violencemedical':            'vt',
                              'violencesports':             'vu',
                              'violenceobjects':            'vk',
                             },
              },
  "rsac":     {'name': 'RSAC',
               'categories': {'violence': 'v',
                              'sex':      's',
                              'nudity':   'n',
                              'language': 'l',
                             },
              },
  "weburbia": {'name': 'Weburbia',
               'categories': {'rating': 's',
                             },
              },
  "vancouver": {'name': 'Vancouver',
               'categories': {'multiculturalism':       'MC',
                              'educationalcontent':     'Edu',
                              'environmentalawareness': 'Env',
                              'tolerance':              'Tol',
                              'violence':               'V',
                              'sex':                    'S',
                              'profanity':              'P',
                              'safety':                 'SF',
                              'canadiancontent':        'Can',
                              'commercialcontent':      'Com',
                              'gambling':               'Gam',
                             },
               },
}


def check_pics (rule, labellist):
    """parse and check PICS labels according to given PicsRule
       return None if no rating is exceeded
       return non-empty match message if some rating exceeds the configured
       PicsRule rating levels
    """
    last = 0
    for mo in ratings(labellist):
        rating = mo.group('rating')
        debug(PICS, "rating %s", rating)
        # the blurb contains the service name and options
        blurb = labellist[last:mo.start()].lower()
        debug(PICS, "blurb %s", blurb)
        last = mo.end()
        # check all in the rule configured PICS services
        for service, options in rule.ratings.items():
            # options has the configured rating values which get
            # compared with the given rating
            if blurb.find(service) != -1:
                # sdata contains category names
                sdata = services[service]
                # check one PICS service
                msg = check_service(rating, sdata['categories'],
                                    sdata['name'], options)
                # stop on the first match
                if msg: return msg
    return None


def check_service (rating, categories, name, options):
    """find given categories in rating and compare the according option
       value with the rating value.
       If one of the ratings exceed its option value, return a non-empty
       message, else return None.
    """
    for category, value in options.items():
        category_label = categories[category]
        msg = check_pics_option(rating, category_label, value,
                                "%s %s" % (name, category));
        # stop on the first match
        if msg: return msg
    return None


def check_pics_option (rating, category_label, option, category):
    """find the given label in rating and compare the value with
       option. If the rating exceeds the option, a non-empty message
       is returned, else None"""
    mo = re.search(r'%s\s+(?P<val>\d+)'%category_label, rating)
    if not mo:
        # label not found
        return None
    # get the rating value
    rating = int(mo.group("val"))
    # XXX we do not support intervals (the PICS standard does)
    # XXX we cast to an integer
    if rating > option:
        return i18n._("PICS %s match") % category
    return None


def _test ():
    from wc.filter.rules.PicsRule import PicsRule
    labellist = """(pics-1.1
"http://www.rsac.org/ratingsv01.html"
 l gen true for "http://www.jesusfilm.org"
 r (n  0 s
    0 v 0 l 0))
"http://www.icra.org/ratingsv02.html"
 l gen true for "http://www.jesusfilm.org"
 r (cz 1 lz 1 nz 1 oh 1 vz 1)
 """
    rule = PicsRule()
    print check_pics(rule, labellist)


if __name__=='__main__':
    _test()

