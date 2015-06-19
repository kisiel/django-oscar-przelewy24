from django import forms
from oscar.core.loading import get_model


class Przelewy24PrepareForm(forms.ModelForm):

    class Meta:
        model = get_model('przelewy24', 'Przelewy24Transaction')
        fields = ('p24_session_id', 'p24_email', 'p24_id_sprzedawcy',
                  'p24_kwota', 'p24_crc', 'p24_return_url_ok',
                  'p24_return_url_error', 'p24_opis')
        widgets = {
            'p24_session_id': forms.HiddenInput(),
            'p24_id_sprzedawcy': forms.HiddenInput(),
            'p24_email': forms.HiddenInput(),
            'p24_kwota': forms.HiddenInput(),
            'p24_crc': forms.HiddenInput(),
            'p24_return_url_ok': forms.HiddenInput(),
            'p24_return_url_error': forms.HiddenInput(),
            'p24_opis': forms.HiddenInput(),
        }
