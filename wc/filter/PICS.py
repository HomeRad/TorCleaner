"""Parse and filter PICS data.
See http://www.w3.org/PICS/labels.html for more info.

the following rating standard associations are supported:

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

import wc
from wc.debug import *

# rating phrase searcher
ratings = re.compile(r'r(atings)?\s*\((?P<rating>[^)]*)\)').finditer

# PICS rating associations and their categories
services = [
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
]

def check_pics (rule, labellist):
    """parse pics labels according to given rule config
       return false if no rating matches
       return match message if some rating exceeds the configured rating level
    """
    last = 0
    for mo in ratings(labellist):
        rating = mo.group('rating')
        debug(NIGHTMARE, "PICS rating", rating)
        # the blurb contains the service name and options
        blurb = labellist[last:mo.start()].lower()
        debug(NIGHTMARE, "PICS blurb", blurb)
        last = mo.end()
        for service, sdata in services.items():
            if service in blurb:
                msg = check_service(rating, sdata['categories'],
                               sdata['name'], rule.options[service])
                if msg: return msg
    return None


def check_service (rating, tags, name, options):
    for category, value in options:
        tag = tags[category]
        msg = check_pics_option(rating, tag, value,
                                "%s %s" % (name, category));
        if msg: return msg
    return None


def check_pics_option (rating, label, option, category) {
    i = rating.find(label)
    if i==-1: return None
    # get the rating value
    rating = rating[i:]
    # remove anything after whitespace
    i = rating.find(" ")
    if i != -1:
        rating = rating[:i]
    if not rating: return None
    # convert the rating value
    if int(rating) > option:
        return i18n._("PICS %s match") % category
    return None


def _test ():
    labellist = """(pics-1.1
"http://www.icra.org/ratingsv02.html"
 l gen true for "http://www.jesusfilm.org"
 r (cz 1 lz 1 nz 1 oh 1 vz 1)
"http://www.rsac.org/ratingsv01.html"
 l gen true for "http://www.jesusfilm.org"
 r (n  0 s
    0 v 0 l 0))"""
    rule = PicsRule()
    print check_pics(rule, labellist)

if __name__=='__main__':
    _test()

