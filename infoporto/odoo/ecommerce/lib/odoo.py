from infoporto.odoo.core.odoo import OdooInstance


class Odoo(object):

    # settings
    def getCurrency(self):
        """ Retrieve currency from Odoo Company settings """
        odoo_core = OdooInstance()

        # company ID should be dynamic
        return odoo_core.read('res.company', 1, ['currency_id'])

    # product.category
    def getAncestors(self, cid):
        """ Retrieve recursively all parents for the given cid """
        odoo_core = OdooInstance()
        res = []
        last_found = cid

        while last_found:
            category = odoo_core.read('product.category', int(last_found), ['id', 'name', 'parent_id'])
            if category['parent_id']:
                last_found = category['parent_id'][0]
            else:
                last_found = False

            res.append(dict(id=category['id'], name=category['name']))

        return reversed(res)

    def getCategory(self, cid):
        odoo_core = OdooInstance()

        category = odoo_core.read('product.category', [int(cid)], ['id', 'name'])

        return category[0]

    def getCategories(self, cid=False):
        odoo_core = OdooInstance()

        if not cid:
            args = [('parent_id', '=', False)]
        else:
            args = [('parent_id', '=', int(cid))]

        ids = odoo_core.search('product.category', args)
        categories = odoo_core.read('product.category', ids, ['id', 'name'])

        return categories

    def getProducts(self, cid=False):
        odoo_core = OdooInstance()

        if not cid:
            args = []
        else:
            args = [('categ_id', '=', int(cid))]

        ids = odoo_core.search('product.product', args)
        products = odoo_core.read('product.product', ids,
                                  ['id', 'name', 'description',
                                   'lst_price', 'image', 'image_medium',
                                   'categ_id', 'taxes_id'])

        for product in products:
            if product['taxes_id']:
                tax = odoo_core.read('account.tax',
                                     int(product['taxes_id'][0]), ['amount'])['amount']
            else:
                tax = 0.0

            product['tax'] = tax
            product = self.sanitizeProduct(product)

        return products

    # product.product
    def getProduct(self, pid):
        odoo_core = OdooInstance()

        product = odoo_core.read('product.product', int(pid),
                                 ['id', 'name', 'description',
                                  'lst_price', 'image', 'image_medium',
                                  'categ_id', 'taxes_id'])

        if product['taxes_id']:
            tax = odoo_core.read('account.tax',
                                 int(product['taxes_id'][0]), ['amount'])['amount']
        else:
            tax = 0.0

        product['tax'] = tax

        return self.sanitizeProduct(product)

    def getInShowcase(self):
        #odoo_core = OdooInstance()
        #TODO: an attribute shoudl be added to Odoo product management
        return self.getProducts()

    def sanitizeProduct(self, p):
        """ Sanitize product for using in templates """

        # Money fix, currency should be get
        from money import Money
        p['price'] = p['lst_price']
        p['lst_price'] = Money(amount=p['lst_price'], currency='EUR')
        p['price_total'] = Money(amount=p['price'] * (1 + p['tax']), currency='EUR')

        p['categ_id'] = p['categ_id'][0]

        # Category norm
        if p['image']:
            p['image'] = ''.join(["data:image/png;base64,", p['image']])

        if p['image_medium']:
            p['image_medium'] = ''.join(["data:image/png;base64,", p['image_medium']])

        return p

    def createSalesOrder(self, params):
        """ Create a partner if the e-mail weren't found, create a Sales Order
            and its Sales Order Line """

        # change params to reflect given data
        odoo_core = OdooInstance()

        # check if user exists ...
        args = [('email', '=', params['user']['email'])]
        ids = odoo_core.search('res.partner', args)

        # ... otherwise create
        if not ids:
            user = dict(name=params['user']['name'],
                        email=params['user']['email'])
            partner_id = odoo_core.create('res.partner', user)

        # build sales order
        so = dict(partner_id=ids[0] or partner_id,
                  state="manual",
                  amount_total=params['total'] * 1.22,
                  amount_tax=params['total'] * 1.22 - params['total'],
                  amount_untaxed=params['total'])
        so_id = odoo_core.create('sale.order', so)

        sol = dict(order_id=so_id,
                   product_uom=1,
                   price_unit=12.0,
                   product_uom_qty=1,
                   state='confirmed',
                   product_id=2,
                   order_parter_id=ids[0],
                   tax_id=[1])

        sol_id = odoo_core.create('sale.order.line', sol)

        #FIXME: taxes?!?

        return sol_id
