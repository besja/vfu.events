from five import grok

import z3c.form

from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from plone.directives import dexterity, form

from vfu.events import MessageFactory as _
from plone.dexterity.content import Item

from vfu.events.utils import validateaddress, list_to_voc, genderConstraint 


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

    pricing = schema.List(title=_(u'Pricing'), required=False, value_type=schema.Choice(source=pricing))
    
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

    def getGender(self, context):
        voc = gender(self)
        terms = self.gender
        result = []
        for i in voc:
           if i.value in terms:
               result.append(context.translate(i.title))
        return ", ".join(result)

    def getPricing(self, context):
        if not self.pricing:
            return ""
        voc = pricing(self)
        terms = self.pricing
        result = []
        for i in voc:
           if i.value in terms:
               result.append(context.translate(i.title))
        return ", ".join(result)
