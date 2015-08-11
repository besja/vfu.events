import re

from five import grok

import z3c.form

from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from plone.directives import dexterity, form

from vfu.events import MessageFactory as _
from vfu.events.config import get_vocabs 
from plone.dexterity.content import Item

def list_to_voc(name):
    vocs = get_vocabs();
    voc = vocs[name]
    terms = []
    for i in voc:
        terms.append(SimpleTerm(value=i[0], title=i[1]))
    return SimpleVocabulary(terms)

def genderConstraint(value):
    if not value:
        raise Invalid(_(u"Select your gender"))
    return True

def pricingConstraint(value):

    if not value:
        raise Invalid(_(u"Select a type of price"))
    return True

# RFC 2822 local-part: dot-atom or quoted-string
# characters allowed in atom: A-Za-z0-9!#$%&'*+-/=?^_`{|}~
# RFC 2821 domain: max 255 characters
_LOCAL_RE = re.compile(r'([A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+'
                     r'(\.[A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+)*|'
                     r'"[^(\|")]*")@[^@]{3,255}$')

# RFC 2821 local-part: max 64 characters
# RFC 2821 domain: sequence of dot-separated labels
# characters allowed in label: A-Za-z0-9-, first is a letter
# Even though the RFC does not allow it all-numeric domains do exist
_DOMAIN_RE = re.compile(r'[^@]{1,64}@[A-Za-z0-9][A-Za-z0-9-]*'
                                r'(\.[A-Za-z0-9][A-Za-z0-9-]*)+$')

def validateaddress(value):

    if not _LOCAL_RE.match(value):
        raise Invalid(_(u'Invalid email address.'))
    if not _DOMAIN_RE.match(value):
        raise Invalid(_(u'Invalid email address.'))
    return True


@grok.provider(IContextSourceBinder)
def gender(context):
    return list_to_voc('gender')

@grok.provider(IContextSourceBinder)
def pricing(context):
    return list_to_voc('pricing')

class IBasicForm(form.Schema):
    lastname = schema.TextLine(title=_(u'Lastname'), required=True)
    firstname = schema.TextLine(title=_(u'Firstname'), required=True)
    gender = schema.List(title=_(u'Gendre'), required=True, value_type=schema.Choice(source=gender), constraint=genderConstraint)
    
    job = schema.TextLine(title=_(u'Job'), required=False)
    organization = schema.TextLine(title=_(u'Organization'), required=False)
    email = schema.TextLine(title=_(u'Email'), required=True, constraint=validateaddress)
    phone = schema.TextLine(title=_(u'Phone'), required=False)
    street = schema.TextLine(title=_(u'Street'), required=True)
    number = schema.TextLine(title=_(u'Number'), required=True)
    zipcode = schema.TextLine(title=_(u'Zipcode'), required=True)
    city = schema.TextLine(title=_(u'City'), required=True)
    country = schema.TextLine(title=_(u'Country'), required=True)

    pricing = schema.List(title=_(u'Pricing'), required=True, value_type=schema.Choice(source=pricing), constraint=pricingConstraint)
    
    comments = schema.Text(title=_(u"Comments"), required=False)

    form.widget(gender=z3c.form.browser.radio.RadioFieldWidget)
    form.widget(pricing=z3c.form.browser.radio.RadioFieldWidget)
    form.fieldset('billing_address',
            label=_(u"Billing address"),
            fields=['street', 'number', 'zipcode', 'city', 'country']
        )
class IRegistration(IBasicForm):
    """
    Registration date
    """
    
    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/expert.xml to define the content type.

    #desc = RichText(title=_(u'Description'), required=True)    
    #text = RichText(title=_(u'Body text'), required=False)


class Registration(Item):
    grok.implements(IRegistration)

    # Add your class methods and properties here

    def Title(self):

        if self.lastname and self.firstname:
            return self.lastname + " " + self.firstname
        else:
            return self.id

    def getGeneder(self):
        voc = gender(self)
        terms = self.gender
        result = []
        for i in voc:
           if i.value in terms:
               result.append(i.title)
        return ", ".join(result)

    def getPricing(self):
        voc = pricing(self)
        terms = self.pricing
        result = []
        for i in voc:
           if i.value in terms:
               result.append(i.title)
        return ", ".join(result)
