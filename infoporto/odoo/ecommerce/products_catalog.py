from five import grok

from plone.dexterity.content import Item

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable

from infoporto.odoo.ecommerce import MessageFactory as _
from odoo_lib import Odoo


class IProductsCatalog(form.Schema, IImageScaleTraversable):
    intro = RichText(
        title=_(u"Intro Text"),
        required=False
    )


class ProductsCatalog(Item):
    grok.implements(IProductsCatalog)
    odoo = Odoo()

    def getCategories(self):
        return self.odoo.getCategories()

    def getInShowcase(self):
        return self.odoo.getInShowcase()


class View(grok.View):
    """ sample view class """
    grok.context(IProductsCatalog)
    grok.require('zope2.View')

    #grok.name('view')
