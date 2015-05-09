from oscar.apps.checkout.app import CheckoutApplication

from .views import Przelewy24PaymentDetailsView


class Przelewy24CheckoutApplication(CheckoutApplication):
    payment_details_view = Przelewy24PaymentDetailsView


application = Przelewy24CheckoutApplication()
