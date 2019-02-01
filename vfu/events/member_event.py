import logging
from five import grok
from zope import schema
from plone.directives import dexterity, form
from plone.dexterity.content import Container

from vfu.events import MessageFactory as _

    
class IVFUMemberEvent(form.Schema):
    """
    Event info
    """

    available = schema.Bool(title=_(u'Available'), required=False, default=True)

class VFUMemberEvent(Container):
    grok.implements(IVFUMemberEvent)

