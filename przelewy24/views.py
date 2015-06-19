import json
import requests
import logging
import hashlib

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import View, TemplateView

from oscar.core.loading import get_class, get_model
from przelewy24 import const, PRZELEWY24_PL, LOGGING_PREFIX


CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
CheckoutSessionData = get_class('checkout.session', 'CheckoutSessionData')
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')
Selector = get_class('partner.strategy', 'Selector')
Przelewy24PrepareForm = get_class('przelewy24.forms', 'Przelewy24PrepareForm')
Basket = get_model('basket', 'Basket')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
Przelewy24Transaction = get_model('przelewy24', 'Przelewy24Transaction')

logger = logging.getLogger(PRZELEWY24_PL)


class Przelewy24PrepareView(OrderPlacementMixin, TemplateView):
    template_name = 'przelewy24/prepare_form.html'

    def _get_basket(self):
        self.restore_frozen_basket()
        self.order_number = self.checkout_session.get_order_number()
        basket = self.request.basket
        self.basket_id = basket.id
        self.order_total = basket.total_incl_tax

        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        logger.info('%s - freezing basket with id: %s.' % (
            LOGGING_PREFIX, self.basket_id))

    def _get_scheme(self):
        return 'https' if self.request.is_secure() else 'http'

    def _get_host(self):
        return self.request.META['HTTP_HOST']

    def _get_absolute_url(self, url):
        return '%s://%s%s' % (self._get_scheme(), self._get_host(), url)

    def _get_p24_return_url_ok(self):
        url = reverse('przelewy24-accept', args=(self.basket_id,))
        return self._get_absolute_url(url)

    def _get_p24_return_url_error(self):
        url = reverse('przelewy24-reject', args=(self.basket_id,))
        return self._get_absolute_url(url)

    def _get_p24_kwota(self):
        return str(int(100 * self.order_total))

    def _get_p24_session_id(self):
        if not hasattr(self, '_p24_session_id'):
            hash_code = hashlib.sha224()
            hash_code.update(str(settings.SECRET_KEY))
            hash_code.update(str(const.P24_VENDOR_ID))
            hash_code.update(str(now()))
            self._p24_session_id = hash_code.hexdigest()
        return self._p24_session_id

    def _get_p24_crc(self):
        if not hasattr(self, '_p24_crc'):
            crc_hash = "%s|%s|%s|%s" % (
                self._get_p24_session_id(), const.P24_VENDOR_ID,
                self._get_p24_kwota(), const.P24_VENDOR_CRC)
            m = hashlib.md5()
            m.update(crc_hash)
            self._p24_crc = m.hexdigest()
        return self._p24_crc

    def _get_p24_email(self):
        return const.P24_VENDOR_EMAIL

    def _get_p24_opis(self):
        return const.P24_OPIS or self.request.user.email

    def _save_p24_transaction(self):
        p24 = Przelewy24Transaction.objects.create(**self._get_form_initial())
        logger.info('%s - saved Przelewy24Transaction with ID: %s' % (
            LOGGING_PREFIX, p24.pk))
        return p24

    def _get_form_initial(self):
        p24_session_id = self._get_p24_session_id()
        p24_crc = self._get_p24_crc()
        p24_kwota = self._get_p24_kwota()
        p24_return_url_ok = self._get_p24_return_url_ok()
        p24_return_url_error = self._get_p24_return_url_error()
        p24_opis = self._get_p24_opis()
        initial = {
            'p24_session_id': p24_session_id,
            'p24_id_sprzedawcy': const.P24_VENDOR_ID,
            'p24_email': self._get_p24_email(),
            'p24_kwota': p24_kwota,
            'p24_crc': p24_crc,
            'p24_return_url_ok': p24_return_url_ok,
            'p24_return_url_error': p24_return_url_error,
            'p24_opis': p24_opis}
        logger.info('%s - initial POST: %s' % (LOGGING_PREFIX,
                                               json.dumps(initial)))
        return initial

    def get_context_data(self, **kwargs):
        context = super(Przelewy24PrepareView, self).get_context_data(**kwargs)
        prepare_form = Przelewy24PrepareForm(initial=self._get_form_initial())
        context.update({
            'prepare_form': prepare_form,
            'p24_url': const.P24_INIT_URL})
        return context

    def get(self, request, *args, **kwargs):
        self._get_basket()
        self._save_p24_transaction()
        return super(Przelewy24PrepareView, self).get(request, *args, **kwargs)


class Przelewy24MixIn(object):
    required_POST_params = []
    required_model_attrs = []
    new_attrs_to_set = []

    def _get_p24_transaction(self):
        if not hasattr(self, '_p24_transaction'):
            p24_session_id = self.request.POST['p24_session_id']
            try:
                p24 = Przelewy24Transaction.objects.get(
                    p24_session_id=p24_session_id,
                    status=const.P24_STATUS_INITIATED)
            except Przelewy24Transaction.DoesNotExist:
                logger.error('P24 - Przelewy24Transaction with ID %s does '
                             'not exist' % p24_session_id)
                raise Http404
            self._p24_transaction = p24
        return self._p24_transaction
    p24_transaction = property(_get_p24_transaction)

    def _check_required_POST_parameters(self):
        post = self.request.POST
        if not all([i in post for i in self.required_POST_params]):
            logger.error('%s - required POST parameter missing' %
                         LOGGING_PREFIX)
            return False
        return True

    def _get_p24_crc2(self):
        post = self.request.POST
        crc_hash = "%s|%s|%s|%s" % (
            self.p24_transaction.p24_session_id,
            post['p24_order_id'],
            self.p24_transaction.p24_kwota,
            const.P24_VENDOR_CRC)
        m = hashlib.md5()
        m.update(crc_hash)
        return m.hexdigest()

    def _verify_p24_crc2(self):
        post = self.request.POST
        p24_crc2_from_post = post['p24_crc']
        if not self.p24_transaction.p24_crc2 == p24_crc2_from_post:
            logger.error('%s - p24_crc2 does not match. %s!=%s' % (
                LOGGING_PREFIX, self.p24_transaction.p24_crc2,
                p24_crc2_from_post))
            return False
        return True

    def _verify_required_model_attrs(self):
        p24 = self.p24_transaction
        post = self.request.POST
        for attr in self.required_model_attrs:
            if not getattr(p24, attr) == post[attr]:
                logger.error('%s - %s does not match. %s!=%s' % (
                    LOGGING_PREFIX, attr,  getattr(p24, attr), post[attr]))
                return False
        return True

    def _verify_p24_response(self):
        if not self._check_required_POST_parameters() or \
                not self._verify_required_model_attrs():
            return False

        p24_crc2 = self._get_p24_crc2()
        p24 = self.p24_transaction
        p24.p24_crc2 = p24_crc2
        if not self._verify_p24_crc2():
            return False

        return True

    def _save_p24_transaction(self, attrs_only=None, additional_attrs=None,
                              commit=True):
        p24 = self.p24_transaction
        post = self.request.POST
        if attrs_only:
            for k, v in attrs_only.items():
                setattr(p24, k, v)
        else:
            for attr in self.new_attrs_to_set:
                setattr(p24, attr, post[attr])
            if additional_attrs:
                for k, v in additional_attrs.items():
                    setattr(p24, k, v)
        if commit:
            p24.save()
        return p24


class Przelewy24AcceptPaymentView(Przelewy24MixIn, PaymentDetailsView):
    required_POST_params = ['p24_order_id', 'p24_kwota', 'p24_crc',
                            'p24_karta', 'p24_id_sprzedawcy',
                            'p24_order_id_full', 'p24_session_id']
    required_model_attrs = ['p24_kwota', 'p24_id_sprzedawcy']
    new_attrs_to_set = ['p24_order_id', 'p24_order_id_full', 'p24_karta']

    def _set_basket(self):
        self.checkout_session = CheckoutSessionData(self.request)
        self.restore_frozen_basket()
        self.basket_id = self.checkout_session.get_submitted_basket_id()
        logger.info('%s - restoring frozen basket with id: %s.' % (
            LOGGING_PREFIX, self.basket_id))

    def _verify_basket_id(self):
        basket_id_from_request = int(self.kwargs.get('basket_id'))
        if not self.basket_id == basket_id_from_request:
            logger.error('%s - basket id does not match. %s!=%s' % (
                LOGGING_PREFIX, self.basket_id, basket_id_from_request))
            return False
        return True

    def _confirm_p24_transaction(self):
        p24 = self.p24_transaction
        url = const.P24_TRANSACTION_URL
        data = {
            'p24_session_id': p24.p24_session_id,
            'p24_order_id': p24.p24_order_id,
            'p24_id_sprzedawcy': p24.p24_id_sprzedawcy,
            'p24_kwota': p24.p24_kwota,
            'p24_crc': p24.p24_crc2
        }
        logger.info('%s - sending confirmation request: %s' % (
            LOGGING_PREFIX, json.dumps(data)))

        response = requests.post(url, data=data)

        logger.info('%s - confirmation response: %s' % (
            LOGGING_PREFIX, response.content))

        confirmation_response = list(response.iter_lines())

        # confirmed
        if response.status_code == 200 and confirmation_response[1] == 'TRUE':
            return True, confirmation_response
        # NOT confirmed
        return False, confirmation_response

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self._set_basket()
        return super(Przelewy24AcceptPaymentView, self).dispatch(
            request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        post = request.POST

        logger.info('%s - accept view. Basket ID: %s POST: %s' % (
            LOGGING_PREFIX, self.basket_id, json.dumps(post)))

        if not self._verify_basket_id() or not self._verify_p24_response():
            self._save_p24_transaction(
                attrs_only={'status': const.P24_STATUS_FAKE})
            messages.error(
                self.request,
                _("%(payment_source)s - transaction incorrect" % {
                    'payment_source': PRZELEWY24_PL}))
            logger.error('%s - transaction incorrect' % (LOGGING_PREFIX,))
            return HttpResponseRedirect(reverse('basket:summary'))

        self._save_p24_transaction(commit=False)

        confirmed, confirmation_response = self._confirm_p24_transaction()
        if not confirmed:
            self._save_p24_transaction(attrs_only={
                'status': const.P24_STATUS_ACCEPTED_NOT_VERIFIED,
                'p24_error_code': confirmation_response[2],
                'p24_error_desc': confirmation_response[3].decode('cp1252'),
            })
            messages.error(
                self.request,
                _("%(payment_source)s - transaction NOT confirmed" %
                  {'payment_source': PRZELEWY24_PL}))
            logger.error('%s - transaction NOT confirmed. p24_session_id:  %s'
                         % (LOGGING_PREFIX, post.get('p24_session_id')))
            return HttpResponseRedirect(reverse('basket:summary'))

        self._save_p24_transaction(attrs_only={
            'status': const.P24_STATUS_ACCEPTED_VERIFIED
        })

        logger.info('%s - transaction verified. p24_session_id:  %s' % (
            LOGGING_PREFIX, post.get('p24_session_id')))
        submission = self.build_submission(basket=request.basket)
        return self.submit(**submission)

    def handle_payment(self, order_number, order_total, **kwargs):
        reference = self.p24_transaction.p24_session_id

        # Payment successful! Record payment source
        source_type, __ = SourceType.objects.get_or_create(
            name=PRZELEWY24_PL)
        source = Source(
            source_type=source_type,
            amount_allocated=order_total.incl_tax,
            reference=reference)
        self.add_payment_source(source)

        # Record payment event
        self.add_payment_event('pre-auth', order_total.incl_tax)


class Przelewy24RejectPaymentView(Przelewy24MixIn, View):
    required_params = ['p24_order_id', 'p24_kwota', 'p24_crc',
                       'p24_id_sprzedawcy', 'p24_error_code',
                       'p24_order_id_full', 'p24_session_id']
    required_model_attrs = ['p24_kwota', 'p24_id_sprzedawcy']
    new_attrs_to_set = ['p24_order_id', 'p24_order_id_full', 'p24_error_code']

    def post(self, request, *args, **kwargs):
        logger.info('P24 - reject view. Basket ID: %s' %
                    kwargs.get('basket_id'))
        basket = get_object_or_404(Basket, id=kwargs['basket_id'],
                                   status=Basket.FROZEN)
        basket.thaw()
        logger.info('P24 - reject view. POST: %s' % json.dumps(request.POST))

        if not self._verify_p24_response():
            messages.error(
                self.request,
                _("%(payment_source)s - transaction incorrect" % {
                    'payment_source': PRZELEWY24_PL}))
            logger.error('%s - transaction FAKE' % (LOGGING_PREFIX,))
            self._save_p24_transaction(
                attrs_only={'status': const.P24_STATUS_FAKE})
            return HttpResponseRedirect(reverse('basket:summary'))

        self._save_p24_transaction(
            additional_attrs={'status': const.P24_STATUS_REJECTED})
        logger.info('%s - transaction rejected. p24_session_id:  %s' % (
            LOGGING_PREFIX, request.POST['p24_session_id']))
        messages.error(
            self.request,
            _("%(payment_source)s - transaction failed" % {
                'payment_source': PRZELEWY24_PL}))
        return HttpResponseRedirect(reverse('basket:summary'))


class Przelewy24AcceptDelayedPaymentView(CheckoutSessionMixin, View):
    #TODO: to be implemented
    pass
