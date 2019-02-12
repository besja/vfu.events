#!/usr/bin/python
# -*- coding: utf8 -*-
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

def validate_privacy(value):
    if not value:
        raise Invalid(_(u'Diese Box muss ausgewählt werden.'))
    return True
    
class IBasicForm(form.Schema):
    gender = schema.List(title=_(u'Gender'), required=True, value_type=schema.Choice(source=gender), constraint=genderConstraint)
    lastname = schema.TextLine(title=_(u'Lastname'), required=True)
    firstname = schema.TextLine(title=_(u'Firstname'), required=True)
    
    
    job = schema.TextLine(title=_(u'Job'), required=False)
    organization = schema.TextLine(title=_(u'Organization'), required=False)
    email = schema.TextLine(title=_(u'Email'), required=True, constraint=validateaddress)
    
    privacy1 = schema.Bool(title=_(u'Politic'), required=True, constraint=validate_privacy)
    privacy2 = schema.Bool(title=_(u'Ich erkläre mich damit einverstanden, dass folgende Daten (Name, Firma) anderen Teilnehmern dieser Veranstaltung (etwa in Form einer Teilnehmerliste) zur Verfügung gestellt werden.'), required=False)
    privacy3 = schema.Bool(title=_(u'Ich erkläre mich mit der Nutzung meiner oben genannten Daten einverstanden, um Einladungen für weitere Veranstaltungen oder um Informationen des VfU zu erhalten.'), required=False)

    form.widget(gender=z3c.form.browser.radio.RadioFieldWidget)

class IMemberEventRegistration(IBasicForm):
    """
    Registration date
    """
    
    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/expert.xml to define the content type.

    #desc = RichText(title=_(u'Description'), required=True)    
    #text = RichText(title=_(u'Body text'), required=False)


class MemberEventRegistration(Item):
    grok.implements(IMemberEventRegistration)

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

    def getPrivacy2(self, context):
        if self.privacy2:
            return _(u'Yes')
        else:
            return _(u'No')
    def getPrivacy3(self, context):
        if self.privacy3:
            return _(u'Yes')
        else:
            return _(u'No')
