from django.db import models

from . import const


class Przelewy24Transaction(models.Model):
    """
        model for storing P24 transaction
    """
    p24_session_id = models.CharField(u"P24 session id", max_length=64)
    p24_id_sprzedawcy = models.CharField(u"Vendor Id", max_length=10)
    p24_email = models.EmailField(u'Vendor email')
    p24_kwota = models.CharField(u"Amount", max_length=10)
    p24_order_id = models.CharField(
        u"Order ID", max_length=100, null=True, blank=True)
    p24_order_id_full = models.CharField(
        u"Order ID Full", max_length=100, null=True, blank=True)

    p24_return_url_ok = models.URLField(u"Return URL OK")
    p24_return_url_error = models.URLField(u"Return URL ERROR")

    p24_karta = models.CharField(
        u"CC?", max_length=10, blank=True, null=True)
    p24_opis = models.TextField(u"Description", null=True, blank=True)

    p24_crc = models.CharField(
        u"CHECKSUM HASH", max_length=32,
        help_text=u'In our request to P24 - will be verified by P24')
    p24_crc2 = models.CharField(
        u"CHECKSUM HASH 2", max_length=32,
        help_text=u'In response from P24 - needs to be verified by us')

    p24_error_code = models.CharField(u"Error code", max_length=7, blank=True)
    p24_error_desc = models.CharField(u"Error description", max_length=255,
                                      null=True, blank=True)

    status = models.IntegerField(
        u"Transaction status",
        default=const.P24_STATUS_INITIATED,
        choices=const.P24_STATUS_CHOICES)

    created_at = models.DateTimeField(u"Created date", auto_now_add=True)
    updated_at = models.DateTimeField(u"Updated date", auto_now=True)

    class Meta:
        ordering = ('-updated_at',)

    def __unicode__(self):
        return u'%s' % self.p24_session_id
