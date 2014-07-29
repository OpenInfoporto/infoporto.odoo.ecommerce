from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from lib.odoo import Odoo
from plone import api

import logging


logger = logging.getLogger("Plone")


class ProductView(BrowserView):
    odoo = Odoo()
    template = ViewPageTemplateFile('products_catalog_templates/product_view.pt')

    def getProduct(self, id):
        return self.odoo.getProduct(id)

    def getAncestors(self):
        #TODO: should be done better
        cid = self.request.get('cid')
        return self.odoo.getAncestors(cid)

    def formatPrice(data):
        return data

    def __call__(self):
        pid = self.request.get('pid')
        self.product = self.getProduct(pid)

        return self.template()


class ProductActions(BrowserView):
    odoo = Odoo()
    template = ViewPageTemplateFile('products_catalog_templates/cart_view.pt')

    def get_elements(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        cart = session.get('cart_elements')

        return cart

    def get_total_price(self):
        from money import Money

        curr = self.odoo.getCurrency()
        total = 0.0
        cart = self.get_elements()
        if cart:
            for el in cart:
                total += float(el['price_total'])

        return Money(amount=total, currency=curr.get('currency_id')[1])

    def addToCart(self, pid):
        cart = []
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        if not session.get("cart_elements"):
            session.set("cart_elements", cart)

        cart = session.get("cart_elements")
        # fetch product
        product = self.odoo.getProduct(pid)

        cart.append(product)

        session.set("cart_elements", cart)

        return "Product %s added to cart" % pid

    def __call__(self):
        pid = self.request.get('pid')
        if pid:
            self.cart = self.addToCart(pid)

        return self.template()


class CheckoutConfirmActions(BrowserView):
    template = ViewPageTemplateFile('products_catalog_templates/checkout_data.pt')

    def get_elements(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        cart = session.get('cart_elements')

        return cart

    def get_total_price(self):
        from money import Money
        #TODO: currency should be param

        total = 0.0
        cart = self.get_elements()
        if cart:
            for el in cart:
                total += float(el['price'])

        return Money(amount=total, currency='EUR')

    def __call__(self):
        return self.template()


class CartActions(BrowserView):

    def emptyCart(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        del session['cart_elements']

    def __call__(self):
        self.emptyCart()
        api.portal.show_message(message='Cart is now empty',
                                request=self.request, type='info')

        return self.request.response.redirect(api.portal.get().absolute_url())


class CheckoutDoActions(BrowserView):
    odoo = Odoo()
    template = ViewPageTemplateFile('products_catalog_templates/checkout_do.pt')

    def __call__(self):
        from lib.paypal import PayPal

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        cart = session.get('cart_elements')

        # parsing cart
        items = []
        total = float(0.0)
        currency = 'EUR'

        for el in cart:
            item = dict(name=el['name'], price=el['price'], sku=el['name'])
            items.append(item)
            total += el['price']
            total = round(total, 2)

        payment = {
            "payment_method": "credit_card",
            "credit_card": {
                "type": self.request.get('type'),
                "number": self.request.get('number'),
                "expire_month": self.request.get('expire_month'),
                "expire_year": self.request.get('expire_year'),
                "cvv2": self.request.get('cvv2'),
                "first_name": self.request.get('first_name'),
                "last_name": self.request.get('last_name'),
                "email": self.request.get('email')},
            "items": items,
            "total": total,
            "currency": currency,
            "description": "This is the payment transaction description."}

        pp = PayPal(params=payment)
        if pp.pay():
            payment['user'] = dict(email=api.user.get_current().email,
                                   name="%s %s" %
                                        (self.request.get('first_name'),
                                         self.request.get('last_name')))

            try:
                self.odoo.createSalesOrder(payment)
                self.emptyCart()
                api.portal.show_message(message='Order confirmed.',
                                        request=self.request, type='info')
            except Exception as e:
                api.portal.show_message(message='Problem creating Sales Orderer',
                                        request=self.request, type='error')
                logger.error("Problem creating Sales Order on Odoo %s " % e)
        else:
            # payment failed, what can I do?
            import pdb; pdb.set_trace()
            api.portal.show_message(message='Problem during payment',
                                    request=self.request, type='error')
            logger.error("Problem during payment")

        return self.template()
