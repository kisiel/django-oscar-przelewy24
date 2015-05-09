from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.apps.dashboard.app import DashboardApplication

from przelewy24.dashboard.views import Przelewy24TransactionListView, \
    Przelewy24TransactionDetailView


class Przelewy24DashboardApplication(DashboardApplication):
    list_view = Przelewy24TransactionListView
    detail_view = Przelewy24TransactionDetailView

    def get_urls(self):
        urls = super(Przelewy24DashboardApplication, self).get_urls()
        urlpatterns = patterns(
            '',
            url(r'^transactions/$', self.list_view.as_view(),
                name='p24-transactions-list'),
            url(r'^transactions/(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='p24-transaction-detail'),
        )
        return self.post_process_urls(urls + urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required


application = Przelewy24DashboardApplication()
