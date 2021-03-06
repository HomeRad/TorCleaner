# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam

from ... import log, LOG_RATING, filter, AppName, Url
from . import ratingformat
from .. import RatingService


class WebCleanerService(RatingService):
    """
    WebCleaner rating service supporting some basic categories:
    violence, sex, language, age.
    """

    def __init__(self):
        """
        Initialize service data and a submit and request CGI url.
        """
        # service name
        self.name = "%s rating service" % AppName
        # service homepage
        self.url = '%s/rating/' % Url,
        # rating formats
        agerange = ratingformat.IntRange(minval=0)
        self.ratingformats = [
            ratingformat.RangeFormat("WC-Age", agerange),
            ratingformat.ValueFormat("WC-Language"),
            ratingformat.ValueFormat("WC-Sex"),
            ratingformat.ValueFormat("WC-Violence"),
        ]
        # submit ratings to service
        self.submit = '%s/submit' % self.url,
        # request ratings from service
        self.request = '%s/request' % self.url,
        self.cache = {}

    def get_ratingformat(self, name):
        name = name.lower()
        for format in self.ratingformats:
            if format.name.lower() == name:
                return format
        return None

    def rating_check(self, limit, rating):
        """Check given rating against limit."""
        for name, value in limit.iteritems():
            format = self.get_ratingformat(name)
            if format is None:
                log.info(LOG_RATING, "Unknown rating %r in %s", name, limit)
                continue
            if name not in rating:
                log.info(LOG_RATING, "Missing rating %r in %s", name, rating)
                continue
            rvalue = rating[name]
            if not format.allowance(rvalue, value):
                msg = "%s limit %r exceeded by %r" % (format, rvalue, value)
                raise filter.FilterRating(msg)

    def rating_compile(self, rating):
        """
        Convert rating values from string representation.
        """
        for format in self.ratingformats:
            name = format.name
            if name not in rating:
                # Use the most restrictive setting as default.
                if format.iterable:
                    value = format.values[0]
                else:
                    value = ratingformat.IntRange(maxval=0)
                rating[name] = value
            elif not format.iterable:
                value = rating[name]
                if isinstance(value, basestring):
                    rating[name] = ratingformat.parse_range(value)


# instantiate the global service
ratingservice = WebCleanerService()
