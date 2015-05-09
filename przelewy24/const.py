from django.conf import settings

P24_VENDOR_ID = getattr(settings, 'P24_VENDOR_ID', '')
P24_VENDOR_NAME = getattr(settings, 'P24_VENDOR_NAME', '')
P24_VENDOR_ADDRESS = getattr(settings, 'P24_VENDOR_ADDRESS', '')
P24_VENDOR_ZIP = getattr(settings, 'P24_VENDOR_ZIP', '')
P24_VENDOR_CITY = getattr(settings, 'P24_VENDOR_CITY', '')
P24_VENDOR_COUNTRY = getattr(settings, 'P24_VENDOR_COUNTRY', '')
P24_VENDOR_EMAIL = getattr(settings, 'P24_VENDOR_EMAIL', '')
P24_VENDOR_CRC = getattr(settings, 'P24_VENDOR_CRC', '')

P24_STATUS_INITIATED = 1
P24_STATUS_FAKE = 2
P24_STATUS_ACCEPTED_VERIFIED = 3
P24_STATUS_ACCEPTED_NOT_VERIFIED = 4
P24_STATUS_REJECTED = 5
P24_STATUS_CHOICES = (
    (P24_STATUS_INITIATED, u'Initiated'),
    (P24_STATUS_FAKE, u'Fake'),  # i.e. not completed POST
    (P24_STATUS_ACCEPTED_VERIFIED, u'Accepted and verified'),
    (P24_STATUS_ACCEPTED_NOT_VERIFIED, u'Accepted, but NOT verified'),
    (P24_STATUS_REJECTED, u'Rejected'),
)

P24_URL_SUBDOMAIN = 'sandbox' if settings.DEBUG else 'secure'
P24_ORIGIN_HOST = 'https://%s.przelewy24.pl' % P24_URL_SUBDOMAIN
P24_INIT_URL = P24_ORIGIN_HOST + '/index.php'
P24_TRANSACTION_URL = P24_ORIGIN_HOST + '/transakcja.php'
# for error simulating (in the sandbox mode) `P24_OPIS` should have one of the
#  following values: TEST_ERR04, TEST_ERR54, TEST_ERR102, TEST_ERR103 or
# TEST_ERR110
P24_OPIS = None
