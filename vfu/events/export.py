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

    def exportCSV(self, container):
        site = component.getSiteManager()
        ptool = getToolByName(site, 'portal_catalog')
        result = ptool(portal_type="vfu.events.registration", 
            path = "/".join(container.getPhysicalPath()), 
            order_on ="getObjPositionInParent", limit=5)
        items = []
        items.append([_(u'lastname'), _(u'firstname'), _(u'gender'), _(u'job'), _(u'organizaton'),  _(u'email'),
             _(u'phone'),  _(u'street'),  _(u'number'),  _(u'zipdcode'),  _(u'city'),  _(u'country'), _(u'pricing'), _(u'comments')])
        for i in result:
            obj = i.getObject()
            items.append([obj.lastname, obj.firstname, obj.getGeneder(), obj.job, obj.organization, obj.email, obj.phone, 
                obj.street, obj.number, obj.zipcode, obj.city, obj.country, obj.getPricing(), obj.comments])

        ramdisk = StringIO.StringIO()
        writer = csv.writer(ramdisk, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(items)
        result = ramdisk.getvalue()
        ramdisk.close()
        return result         
        

    def __call__(self):
        return self.export()
