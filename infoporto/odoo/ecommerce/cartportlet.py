from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from infoporto.odoo.ecommerce import MessageFactory as _


class ICartPortlet(IPortletDataProvider):

    header_title = schema.TextLine(title=_(u"Portlet Header"),
                                   description=_(u"A text for the portlet header"),
                                   required=True)


class Assignment(base.Assignment):
    implements(ICartPortlet)

    def __init__(self, header_title=''):
        self.header_title = header_title

    @property
    def title(self):
        return "Cart"


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('browser/cartportlet.pt')


class AddForm(base.AddForm):
    form_fields = form.Fields(ICartPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ICartPortlet)
