from django import forms
from django.utils.translation import gettext_lazy as _

class LanguageForm(forms.Form):
    language = forms.ChoiceField(
        choices=[('en', _('English')), ('ar', _('Arabic'))],
        label=_('Language')
    )
