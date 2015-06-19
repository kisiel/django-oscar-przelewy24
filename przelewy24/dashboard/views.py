from django.views import generic
from oscar.core.loading import get_model


class Przelewy24TransactionListView(generic.ListView):
    model = get_model('przelewy24', 'Przelewy24Transaction')
    template_name = 'przelewy24/dashboard/transaction_list.html'


class Przelewy24TransactionDetailView(generic.DetailView):
    model = get_model('przelewy24', 'Przelewy24Transaction')
    template_name = 'przelewy24/dashboard/transaction_detail.html'
