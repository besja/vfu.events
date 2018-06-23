#!/usr/bin/python
# -*- coding: utf8 -*-
import random
import zope.schema
import zope.interface
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility, getMultiAdapter

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as Zope3PageTemplateFile

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.interfaces.controlpanel import IMailSchema

from Products.statusmessages.interfaces import IStatusMessage


import z3c.form
import plone.z3cform.templates
from plone.registry.interfaces import IRegistry

from smtplib import SMTPException, SMTPRecipientsRefused

from vfu.events import MessageFactory as _
from vfu.events.utils import trusted
from vfu.events.roundtable_registration import IRoundtableRegistrationForm

from plone.autoform.form import AutoExtensibleForm

class RoundtableRegistrationForm(z3c.form.form.Form):
    """ Display event with form """

    template = Zope3PageTemplateFile("templates/roundtable_registration_form.pt")

    fields = z3c.form.field.Fields(IRoundtableRegistrationForm)

    ignoreContext = True

    enable_unload_protection  = False

    output = None

    ### ! fieldeset 

    fields['gender'].widgetFactory = z3c.form.browser.radio.RadioFieldWidget
    fields['title_of_person'].widgetFactory = z3c.form.browser.radio.RadioFieldWidget
    fields['pricing'].widgetFactory = z3c.form.browser.radio.RadioFieldWidget
    fields['participation'].widgetFactory = z3c.form.browser.checkbox.CheckBoxFieldWidget
    #fields['accomadation'].widgetFactory = z3c.form.browser.checkbox.CheckBoxFieldWidget
    fields['dinner'].widgetFactory = z3c.form.browser.checkbox.SingleCheckBoxFieldWidget
    fields['vegetarian'].widgetFactory = z3c.form.browser.checkbox.SingleCheckBoxFieldWidget
    #fields['workshops'].widgetFactory = z3c.form.browser.checkbox.CheckBoxFieldWidget
    #fields['arrival'].widgetFactory = z3c.form.browser.radio.RadioFieldWidget
    #fields['privacy1'].widgetFactory = z3c.form.browser.checkbox.SingleCheckBoxFieldWidget
    

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)
                   
    def updateWidgets(self):
      
        super(RoundtableRegistrationForm, self).updateWidgets()


        self.widgets['privacy1'].field.description=_(u'Ich habe die Angaben zum <a href="https://vfu.de/datenschutzerklaerung">Datenschutz</a> gelesen und stimme der vorübergehenden Speicherung meiner Daten zu.') 

        if not self.context.dinner_available: 
            self.widgets["dinner"].mode =  z3c.form.interfaces.HIDDEN_MODE
        
        if self.context.dinner_description: 
            self.fields['dinner'].field.description = self.context.dinner_description    

        #if self.context.workshops_description:
        #    self.fields['workshops'].field.description = self.context.workshops_description    

        if not self.context.dinner_available or not self.context.vegfood_available: 
            self.widgets["vegetarian"].mode =  z3c.form.interfaces.HIDDEN_MODE

        #workshops = self.context.getWorkshopsList()

        #if len(workshops) == 0: 
        #    self.widgets["workshops"].mode =  z3c.form.interfaces.HIDDEN_MODE

    @z3c.form.button.buttonAndHandler(_(u"Save"), name='submit')
    def submit(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = _(u"Please correct errors")
            return

        folder = self.context

        id = str(random.randint(0, 99999999))

        new_obj = _createObjectByType("vfu.events.roundtableregistration", folder, id, lastname = data['lastname'], 
            firstname = data['firstname'], gender = data['gender'], title_of_person = data['title_of_person'], job = data['job'], organization = data['organization'], 
            email = data['email'], phone = data['phone'],  street = data['street'],  number = data['number'],  
            zipcode = data['zipcode'], city = data['city'], country = data['country'], pricing = data['pricing'], 
            participation = data['participation'],  dinner = data['dinner'], 
            vegetarian = data['vegetarian'],  
            comments = data['comments'])

        portal = getToolByName(self, 'portal_url').getPortalObject()
        encoding = portal.getProperty('email_charset', 'utf-8')

        trusted_template = trusted(portal.registration_roundtable_email)
        mail_text = trusted_template(
            self, charset=encoding, reg_data = new_obj, event = self.context)

        subject = self.context.translate(_(u"New registration"))
        m_to = data['email']

        ## notify admin about new registration
  
        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(encoding)

        host = getToolByName(self, 'MailHost')

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        m_from = mail_settings.email_from_address

        try:
            host.send(mail_text, m_to, m_from, subject=subject,
                      charset=encoding, immediate=True, msg_type="text/html")

        except SMTPRecipientsRefused:

            raise SMTPRecipientsRefused(
                _(u'Recipient address rejected by server.'))

        except SMTPException as e:
            raise(e)
        
        IStatusMessage(self.request).add(_(u"Submit complete"), type='info')
        return self._redirect(target=self.context.absolute_url())
   

form_frame = plone.z3cform.layout.wrap_form(RoundtableRegistrationForm, index=FiveViewPageTemplateFile("templates/layout.pt"))