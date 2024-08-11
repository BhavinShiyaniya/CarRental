import django_filters
from django_filters import DateFilter, CharFilter, ModelChoiceFilter

from car.models import Car, CarHoldTime, Rent

class BookingsListFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="pickup_datetime", lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name="pickup_datetime", lookup_expr='lte', label='Completion Date')

    class Meta:
        model = Rent
        fields = ("pickup_datetime",)
        # exclude = ['car', 'user', 'drop_datetime', 'total_hours', 'total_fare', 'booking_status', 'payment_status']

        # widgets = {
        #     'car': forms.HiddenInput(attrs={'class': 'form-control'}),
        #     'pickup_datetime': forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
        #     'drop_datetime': forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'})
        # }