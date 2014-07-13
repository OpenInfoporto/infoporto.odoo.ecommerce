from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from lib.odoo import Odoo


class CategoryView(BrowserView):
    odoo = Odoo()
    template = ViewPageTemplateFile('products_catalog_templates/category_view.pt')

    def getAncestors(self):
        #TODO: should be done better
        cid = self.request.get('cid')
        return self.odoo.getAncestors(cid)

    def getCategory(self, id):
        return self.odoo.getCategory(id)

    def getCategories(self, id):
        return self.odoo.getCategories(id)

    def getProducts(self, id):
        return self.odoo.getProducts(id)

    def __call__(self):
        cid = self.request.get('cid')

        self.current = self.getCategory(cid)
        self.categories = self.getCategories(cid)
        self.products = self.getProducts(cid)

        return self.template()
