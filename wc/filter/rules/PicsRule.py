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

from UrlRule import UrlRule
from wc import i18n
from wc.XmlUtils import xmlify, unxmlify

# PICS ratings (default to zero which means disabled)
_default_ratings = {
  "safesurf": {'agerange':                0,
               'profanity':               0,
               'heterosexualthemes':      0,
               'homosexualthemes':        0,
               'nudity':                  0,
               'violence':                0,
               'sexviolenceandprofanity': 0,
               'intolerance':             0,
               'druguse':                 0,
               'otheradultthemes':        0,
               'gambling':                0,
              },
  "evaluweb": {'agerange': 0,},
  "microsys": {'sexrating':   0,
               'otherrating': 0,
              },
  "icra":     {'language':                   0,
               'chat':                       0,
               'moderatedchat':              0,
               'languageprofanity':          0,
               'languagemildexpletives':     0,
               'nuditygraphic':              0,
               'nuditymalegraphic':          0,
               'nudityfemalegraphic':        0,
               'nuditytopless':              0,
               'nuditybottoms':              0,
               'nuditysexualacts':           0,
               'nudityobscuredsexualacts':   0,
               'nuditysexualtouching':       0,
               'nuditykissing':              0,
               'nudityartistic':             0,
               'nudityeducational':          0,
               'nuditymedical':              0,
               'drugstobacco':               0,
               'drugsalcohol':               0,
               'drugsuse':                   0,
               'gambling':                   0,
               'weaponuse':                  0,
               'intolerance':                0,
               'badexample':                 0,
               'pgmaterial':                 0,
               'violencerape':               0,
               'violencetohumans':           0,
               'violencetoanimals':          0,
               'violencetofantasy':          0,
               'violencekillinghumans':      0,
               'violencekillinganimals':     0,
               'violencekillingfantasy':     0,
               'violencejuryhumans':         0,
               'violencejuryanimals':        0,
               'violencejuryfantasy':        0,
               'violenceartistic':           0,
               'violenceeducational':        0,
               'violencemedical':            0,
               'violencesports':             0,
               'violenceobjects':            0,
              },
  "rsac":     {'violence': 0,
               'sex':      0,
               'nudity':   0,
               'language': 0,
              },
  "weburbia": {'rating': 0,
              },
  "vancouver": {'multiculturalism':       0,
                'educationalcontent':     0,
                'environmentalawareness': 0,
                'tolerance':              0,
                'violence':               0,
                'sex':                    0,
                'profanity':              0,
                'safety':                 0,
                'canadiancontent':        0,
                'commercialcontent':      0,
                'gambling':               0,
               },
}

class PicsRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, oid=0):
        UrlRule.__init__(self, title=title, desc=desc,disable=disable,oid=oid)
        self.ratings = {}
        self.service = None
        self.category = None


    def fill_attrs (self, attrs, name):
        if name=='pics':
            UrlRule.fill_attrs(self, attrs, name)
        elif name=='service':
            self.service = unxmlify(attrs.get('name')).encode('iso8859-1')
            self.ratings[service] = {}
        elif name=='category':
            assert self.service
            self.category = unxmlify(attrs.get('name')).encode('iso8859-1')
        else:
            raise ValueError(i18n._("Invalid pics rule tag name `%s',"+\
                                    " check your configuration")%name)


    def fill_data (self, data, name):
        data = unxmlify(data).encode('iso8859-1')
        if name=='category':
            assert self.service
            assert self.category
            assert self.ratings.has_key(self.service)
            self.ratings[self.service][self.category] = int(data)
        else:
            # ignore other content
            pass

    def fromFactory (self, factory):
        return factory.fromPicsRule(self)
