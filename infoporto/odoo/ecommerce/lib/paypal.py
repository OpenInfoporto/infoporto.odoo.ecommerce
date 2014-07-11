import paypalrestsdk
import logging


logger = logging.getLogger("Plone")


class PayPal(object):

    def __init__(self, params):
        self.params = params
        self.paypalrestsdk = paypalrestsdk.configure({
            "mode": "sandbox",
            "client_id": "Afx4RhC9wJrcN2paz0hBJcCIzJE_VbqITVe7XAlFZ8ZgLfVP9jYg0EFHANCB",
            "client_secret": "EHLN1RBPP55QbVHcxtojH-nQ_oaILu41j5h0oan2hfgFcIwpeYzK0DDq-RIf"})

    def buildPayment(self):
        logger.info("Reached buildPayment()")

        params = self.params
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": params['payment_method'],
                "funding_instruments": [{
                    "credit_card": params['credit_card']}]},
            "transactions": [{
                "item_list": {
                    "items": params['items']
                },
                "amount": {
                    "total": params['total'],
                    "currency": params['currency'],
                },
                "description": params['description']
            }]})

        return payment

    def pay(self):
        payment = self.buildPayment()

        if payment.create():
            # should create a payment on Odoo
            logger.info("Payment ID: %s completed" % 'TEST')
        else:
            logger.warn("Payment ID: %s NOT completed" % 'TEST')

        return payment
