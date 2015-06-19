from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt
from oscar.core.loading import get_class


Przelewy24PrepareView = get_class(
    'przelewy24.views', 'Przelewy24PrepareView')
Przelewy24AcceptPaymentView = get_class(
    'przelewy24.views', 'Przelewy24AcceptPaymentView')
Przelewy24RejectPaymentView = get_class(
    'przelewy24.views', 'Przelewy24RejectPaymentView')
Przelewy24AcceptDelayedPaymentView = get_class(
    'przelewy24.views', 'Przelewy24AcceptDelayedPaymentView')


urlpatterns = patterns(
    '',
    url(r'^prepare/$',
        Przelewy24PrepareView.as_view(),
        name='przelewy24-prepare'),
    url(r'accept/(?P<basket_id>\d+)/$',
        csrf_exempt(Przelewy24AcceptPaymentView.as_view()),
        name='przelewy24-accept'),
    url(r'reject/(?P<basket_id>\d+)/$',
        csrf_exempt(Przelewy24RejectPaymentView.as_view()),
        name='przelewy24-reject'),
    url(r'accept-delayed/(?P<basket_id>\d+)/$',
        csrf_exempt(Przelewy24AcceptDelayedPaymentView.as_view()),
        name='przelewy24-accept-delayed'),
)
