import csv
import StringIO

from zope import component

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from vfu.events import MessageFactory as _


class ExportRegistrations(BrowserView):
    """A view to export registration data
    """

    def export(self):
        container = self.context

        result = self.exportCSV(container)
        request = self.request
        coding = 'utf-8'
        setheader = request.RESPONSE.setHeader
        setheader('Content-Length', len(result))

        setheader('Content-Type', 'text/x-comma-separated-values; charset=%s' % coding)
         
        setheader('Content-Disposition', 'filename=export%s.csv' % container.id)   
        return result
    def encode(self, data):
        j = 0
        for i in data:
            if i:
                data[j] = i.encode('utf-8')
            else:
                data[j] = ''.encode('utf-8')

            j+=1
        return data

    def exportCSV(self, container):
        site = component.getSiteManager()
        ptool = getToolByName(site, 'portal_catalog')
        result = ptool(portal_type="vfu.events.registration", 
            path = "/".join(container.getPhysicalPath()), 
            order_on ="getObjPositionInParent", limit=5)
        items = []
        headers = [
                self.context.translate(_(u'lastname')), 
                self.context.translate(_(u'firstname')), 
                self.context.translate(_(u'gender')), 
                self.context.translate(_(u'job')), 
                self.context.translate(_(u'organization')),  
                self.context.translate(_(u'email')),
                self.context.translate(_(u'phone')),  
                self.context.translate(_(u'street')),  
                self.context.translate(_(u'number')),  
                self.context.translate(_(u'zipdcode')),  
                self.context.translate(_(u'city')),  
                self.context.translate(_(u'country')), 
                self.context.translate(_(u'pricing')), 
                self.context.translate(_(u'comments'))
                ]
        headers = self.encode(headers)
        items.append(headers)

        for i in result:
            obj = i.getObject()
            gender = obj.getGender(self.context)
            pricing = obj.getPricing(self.context)
            data = [obj.lastname, 
                    obj.firstname, 
                    gender,  
                    obj.job, 
                    obj.organization, 
                    obj.email, 
                    obj.phone, 
                    obj.street, 
                    obj.number, 
                    obj.zipcode, 
                    obj.city, 
                    obj.country, 
                    pricing, 
                    obj.comments] 

            data = self.encode(data)
            items.append(data)

        ramdisk = StringIO.StringIO()
        writer = csv.writer(ramdisk, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(items)
        result = ramdisk.getvalue()
        ramdisk.close()
        return result         
        

    def __call__(self):
        return self.export()
