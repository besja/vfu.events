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
from vfu.events.member_event_registration import IBasicForm 

class RegistrationForm(z3c.form.form.Form):
    """ Display event with form """

    template = Zope3PageTemplateFile("templates/member_event_registration_form.pt")

    fields = z3c.form.field.Fields(IBasicForm)

    ignoreContext = True

    enable_unload_protection  = False

    output = None

    ### ! fieldeset 

    fields['gender'].widgetFactory = z3c.form.browser.radio.RadioFieldWidget

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)

    @z3c.form.button.buttonAndHandler(_(u"Save"), name='submit')
    def submit(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = _(u"Please correct errors")
            return

        folder = self.context

        id = str(random.randint(0, 99999999))

        new_obj = _createObjectByType("vfu.events.member_event_registration", folder, id, gender = data['gender'], lastname = data['lastname'], 
            firstname = data['firstname'], job = data['job'], organization = data['organization'], 
            email = data['email'], privacy2 = data['privacy2'], privacy3 = data['privacy3'], privacy1 = data['privacy1'])

        portal = getToolByName(self, 'portal_url').getPortalObject()
        encoding = portal.getProperty('email_charset', 'utf-8')

        trusted_template = trusted(portal.member_event_registration_email)
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
   

form_frame = plone.z3cform.layout.wrap_form(RegistrationForm, index=FiveViewPageTemplateFile("templates/layout.pt"))