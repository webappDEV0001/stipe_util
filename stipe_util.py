import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


class StripePayment(object):
    def __init__(self, customer_code, user=None):
        self.customer_code = customer_code
        self.user = user

    def retrieve_customer(self):
        if self.customer_code:
            customer = stripe.Customer.retrieve(self.customer_code)
        else:
            latest_transaction = self.user.current_payment_transaction()
            if latest_transaction:
                try:
                    subscription = stripe.Subscription.retrieve(latest_transaction.transaction_id)
                    customer = stripe.Customer.retrieve(subscription.customer)
                    self.customer_code = customer['id']
                except:
                    customer = None
            else:
                customer = None

        return customer

    def get(self, card_id=None):
        customer = self.retrieve_customer()

        response = {
            'cards': [],
            'default_card': None
        }

        if customer and card_id:
            return customer['default_source']
        elif customer:
            cards = stripe.Customer.list_sources(self.customer_code, object="card", limit=100)
            response['cards'] = cards['data']
            response['default_card'] = customer['default_source']

        return response

    def add(self, token):
        customer = self.retrieve_customer()

        response = {
            'cards': [],
            'default_card': None
        }

        if customer:
            try:
                card_data = stripe.Customer.create_source(self.customer_code, source=token)
                return card_data
            except stripe.CardError as err:
                return {}

        return response

    def delete(self, card_id):
        customer = self.retrieve_customer()

        if customer:
            try:
                s_response = stripe.Customer.delete_source(self.customer_code, card_id)
                if s_response['deleted']:
                    return True
            except:
                pass

        return False

    def make_primary(self, card_id):
        customer = self.retrieve_customer()

        if customer:
            try:
                s_response = stripe.Customer.modify(self.customer_code, default_source=card_id)
                return True
            except:
                pass

        return False
