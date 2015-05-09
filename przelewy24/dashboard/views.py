from django.views import generic

from przelewy24.models import Przelewy24Transaction


class Przelewy24TransactionListView(generic.ListView):
    model = Przelewy24Transaction
    template_name = 'przelewy24/dashboard/transaction_list.html'


class Przelewy24TransactionDetailView(generic.DetailView):
    model = Przelewy24Transaction
    template_name = 'przelewy24/dashboard/transaction_detail.html'
