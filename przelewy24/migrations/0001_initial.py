# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Przelewy24Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p24_session_id', models.CharField(max_length=64, verbose_name='P24 session id')),
                ('p24_id_sprzedawcy', models.CharField(max_length=10, verbose_name='Vendor Id')),
                ('p24_email', models.EmailField(max_length=75, verbose_name='Vendor email')),
                ('p24_kwota', models.CharField(max_length=10, verbose_name='Amount')),
                ('p24_order_id', models.CharField(max_length=100, null=True, verbose_name='Order ID', blank=True)),
                ('p24_order_id_full', models.CharField(max_length=100, null=True, verbose_name='Order ID Full', blank=True)),
                ('p24_return_url_ok', models.URLField(verbose_name='Return URL OK')),
                ('p24_return_url_error', models.URLField(verbose_name='Return URL ERROR')),
                ('p24_karta', models.CharField(max_length=10, null=True, verbose_name='CC?', blank=True)),
                ('p24_opis', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('p24_crc', models.CharField(help_text='In our request to P24 - will be verified by P24', max_length=32, verbose_name='CHECKSUM HASH')),
                ('p24_crc2', models.CharField(help_text='In response from P24 - needs to be verified by us', max_length=32, verbose_name='CHECKSUM HASH 2')),
                ('p24_error_code', models.CharField(max_length=7, verbose_name='Error code', blank=True)),
                ('p24_error_desc', models.CharField(max_length=255, null=True, verbose_name='Error description', blank=True)),
                ('status', models.IntegerField(default=1, verbose_name='Transaction status', choices=[(1, 'Initiated'), (2, 'Fake'), (3, 'Accepted and verified'), (4, 'Accepted, but NOT verified'), (5, 'Rejected')])),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
            ],
            options={
                'ordering': ('-updated_at',),
            },
            bases=(models.Model,),
        ),
    ]
