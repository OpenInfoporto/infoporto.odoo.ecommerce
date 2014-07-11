from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from odoo_lib import Odoo


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
        #TODO: currency should be param

        total = 0.0
        cart = self.get_elements()
        if cart:
            for el in cart:
                total += float(el['lst_price'])

        return Money(amount=total, currency='EUR')

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


class CheckoutActions(BrowserView):
    template = ViewPageTemplateFile('products_catalog_templates/checkout.pt')

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
        pid = self.request.get('pid')
        if pid:
            self.cart = self.addToCart(pid)

        return self.template()


class CheckoutConfirmActions(BrowserView):
    template = ViewPageTemplateFile('products_catalog_templates/checkout_data.pt')

    def __call__(self):
        return self.template()


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
            # payment succeded, creating sales order in Odoo
            import pdb; pdb.set_trace()
            odoo.createSalesOrder(payment)
        else:
            # payment failed, what can I do?
            import pdb; pdb.set_trace()

        return self.template()
