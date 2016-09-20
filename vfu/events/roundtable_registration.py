import re

from five import grok

import z3c.form

from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName

from plone.directives import dexterity, form
from plone.dexterity.content import Item

from vfu.events import MessageFactory as _
from vfu.events.config import get_vocabs 
from vfu.events.utils import validateaddress, list_to_voc, genderConstraint 
from plone.autoform import directives

import collections

@grok.provider(IContextSourceBinder)
def gender(context):
    return list_to_voc('gender')

@grok.provider(IContextSourceBinder)
def pricing(context):
    return list_to_voc('pricing_roundtable')

@grok.provider(IContextSourceBinder)
def participation(context):

    dates = context.getEventDates()
    terms  = []
   
    for i in dates:
        terms.append(SimpleTerm(value=i, title=i))
    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def accomadation(context):

    dates = context.getAccomadationDates()
    terms  = []
   
    for i in dates:
        terms.append(SimpleTerm(value=i, title=i))
    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def workshops(context): 
    options  = context.getWorkshopsList()

    options = collections.OrderedDict(sorted(options.items()))

    terms = []
    for i in options:
        terms.append(SimpleTerm(value=i, title=options[i].encode('utf-8')))

    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def arrival(context):
    return list_to_voc('arrival')

def validate_choice(value):
    if len(value) == 0: 
        raise Invalid(_(u'Select at least a one date'))
    return True

class IRoundtableRegistrationForm(form.Schema):
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
    
    participation= schema.List(title=_(u'Participation'), description=_(u'Select one or both dates'), required=True, value_type=schema.Choice(source=participation) ,  constraint=validate_choice)

    accomadation= schema.List(title=_(u'Accomadation'), description=_(u'Select an accomadation date'), required=False, value_type=schema.Choice(source=accomadation))

    dinner = schema.Bool(title=_(u'Dinner'), required=False)

    vegetarian = schema.Bool(title=_(u'Vegetarian food'), required=False)

    intolerances = schema.Text(title=_(u"Intolerances / incompatibility"), required=False)

    workshops = schema.List(title=_(u'Workshops'), description=_(u'Select workshops to participate'), required=False, value_type=schema.Choice(source=workshops))
    
    arrival = schema.List(title=_(u'Arrival by'), required=False, value_type=schema.Choice(source=arrival))

    comments = schema.Text(title=_(u"Comments"), required=False)

    form.widget(gender=z3c.form.browser.radio.RadioFieldWidget)
    form.widget(pricing=z3c.form.browser.radio.RadioFieldWidget)

    form.widget(participation=z3c.form.browser.checkbox.CheckBoxFieldWidget)
    form.widget(accomadation=z3c.form.browser.checkbox.CheckBoxFieldWidget)
    form.widget(workshops=z3c.form.browser.checkbox.CheckBoxFieldWidget)

    form.fieldset('billing_address',
            label=_(u"Billing address"),
            fields=['street', 'number', 'zipcode', 'city', 'country']
        )

class IRoundtableRegistration(IRoundtableRegistrationForm):
    """
    Registration date
    """
    
    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/expert.xml to define the content type.

    #desc = RichText(title=_(u'Description'), required=True)    
    #text = RichText(title=_(u'Body text'), required=False)
    #form.widget(participation=z3c.form.browser.checkbox.CheckBoxWidget)

class RoundtableRegistration(Item):
    grok.implements(IRoundtableRegistration)

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

    def getParticipation(self, context):
        return ", ".join(self.participation)

    def getAccomadation(self, context):
        return ", ".join(self.accomadation)

    def getArrival(self, context):
        if not self.arrival:
            return ""
        voc = arrival(self)
        terms = self.arrival
        result = []
        for i in voc:
           if i.value in terms:
               result.append(context.translate(i.title))
        return ", ".join(result)
    def getDinner(self, context):
        if self.dinner:
            return _(u'Yes')
        else:
            return _(u'No')
    def getVegetarian(self, context):
        if self.vegetarian:
            return _(u'Yes')
        else:
            return _(u'No')

    def getWorkshopsValues(self, context):
        result = []
        workshops_dict = self.aq_parent.getWorkshopsList()
        if self.workshops:
            for i in self.workshops:
                if workshops_dict.has_key(i):
                    result.append(workshops_dict[i])
        return ', '.join(result)
