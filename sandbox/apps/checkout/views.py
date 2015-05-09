from django.core.urlresolvers import reverse

from oscar.apps.checkout import views
from oscar.apps.checkout.views import RedirectRequired


class Przelewy24PaymentDetailsView(views.PaymentDetailsView):
    preview = True

    def handle_payment(self, order_number, total, **kwargs):
        # Talk to payment gateway.  If unsuccessful/error, raise a
        # PaymentError exception which we allow to percolate up to be caught
        # and handled by the core PaymentDetailsView.
        # reference = api.pre_auth(order_number, total.incl_tax,
        # kwargs['bankcard'])
        raise RedirectRequired(reverse('przelewy24-prepare'))
