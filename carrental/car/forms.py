from django import forms
from django.forms import ModelForm
from django.db import transaction
from user.models import User
from car.models import Car, CarImage, Rent

class RentForm(ModelForm):
    '''Booking create form for cardetail page'''
    class Meta:
        model = Rent
        fields = ('car', 'pickup_datetime', 'drop_datetime', 'total_fare', 'total_hours')

        widgets = {
            'car': forms.HiddenInput(),
            'total_fare': forms.TextInput(attrs={'readonly': 'true', 'class': 'form-control'}),
            'total_hours': forms.TextInput(attrs={'readonly': 'true', 'class': 'form-control'}),
            'pickup_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
            'drop_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'})
        }



    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['car'].disabled = True
    #     self.fields['pickup_datetime'].disabled = True
    #     self.fields['drop_datetime'].disabled = True
    #     self.fields['total_fare'].disabled = True

    # @transaction.atomic
    # def save(self):
    #     rent = super().save(commit=False)
    #     rent.user = self.request.user
    #     rent.save()
    #     return rent

class CarSearchForm(forms.Form):
    '''car search form for index and listing page'''
    start_datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}))
    end_datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}))
