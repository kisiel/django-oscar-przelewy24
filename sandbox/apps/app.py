from oscar.app import Shop

from .checkout.app import application as checkout_app
from przelewy24.dashboard.app import application as dashboard_app


class Przelewy24Shop(Shop):
    checkout_app = checkout_app
    dashboard_app = dashboard_app


shop = Przelewy24Shop()
