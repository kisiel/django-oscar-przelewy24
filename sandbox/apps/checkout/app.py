from oscar.apps.checkout.app import CheckoutApplication
from oscar.core.loading import get_class


class Przelewy24CheckoutApplication(CheckoutApplication):
    payment_details_view = get_class(
        'apps.checkout.views', 'Przelewy24PaymentDetailsView')


application = Przelewy24CheckoutApplication()
