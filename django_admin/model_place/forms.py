from django import forms
from model_place.models import Mailings


class MailingsForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}), label="Содержание")
    mail_date = forms.DateField(label="Дата рассылки", widget=forms.SelectDateWidget)
    mail_time = forms.TimeField(label="Время рассылки", widget=forms.TextInput(attrs={'type': 'time'}))

    class Meta:
        model = Mailings
        fields = ['content', 'image', 'video', 'mail_date', 'mail_time']
