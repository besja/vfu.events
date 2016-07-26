import logging
from five import grok
from zope import schema
from plone.directives import dexterity, form
from plone.dexterity.content import Container
from zope.interface import invariant, Invalid

from datetime import timedelta  

from vfu.events import MessageFactory as _

from vfu.events.utils import daterange

from plone.api.portal import get_localized_time
import re

def validate_workshops(value):
    if value:
        lines = value.split('\n')
        p = re.compile('[0-9]+\|.+$')
        for l in lines:
            if not p.match(l): 
                raise Invalid(_(u'Invalid value for workshops'))
    return True

class IVFURoundtableEvent(form.Schema):
    """
    Roundtable info
    """

    available = schema.Bool(title=_(u'Available'), required=False, default=True)

    start = schema.Date(title=_(u'Start date'), required=True)
    end = schema.Date(title=_(u'End date'), required=True)

    accomadation_start = schema.Date(title=_(u'Accomadation start date'), required=True)
    accomadation_end = schema.Date(title=_(u'Accomadation end date'), required=True)

    dinner_available  = schema.Bool(title=_(u'Is dinner available?'), required=False, default=True)
    vegfood_available  = schema.Bool(title=_(u'Is vegeterian food available?'), required=False, default=True)
    dinner_description = schema.Text(title=_(u"Description for dinner"), required=False)

    workshops = schema.Text(title=_(u"Workshops"), description=_(u"One per line. Format: number|name. For example: 1|Workshop1"), required=False, constraint=validate_workshops)
    workshops_description = schema.Text(title=_(u"Description for workshops"), required=False)


class VFURoundtableEvent(Container):
    grok.implements(IVFURoundtableEvent)

    def getEventDates(self):

    	start = self.start
    	end = self.end
        options = []
    	dates = daterange(start, end + timedelta(days=1) ) 
        for single_date in dates:
            options.append(get_localized_time(single_date))
    	return options

    def getAccomadationDates(self): 
        start = self.accomadation_start
        end = self.accomadation_end
        options = []
        dates = daterange(start,  end + timedelta(days=1) ) 
        for single_date in dates:
            options.append(get_localized_time(single_date))
        return options
    def getWorkshopsList(self):

        options = {}
        if self.workshops: 
            lines = self.workshops.split('\n')
            for l in lines:
                key, value = l.split("|")
                options.update({key:value})
        return options
