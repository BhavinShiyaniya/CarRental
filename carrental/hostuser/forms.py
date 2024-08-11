from typing import Any
from django import forms
from django.forms import ModelForm
from car.models import Car, CarImage, Rent, CarHoldTime
from user.models import User
from django.core.exceptions import ValidationError

class CarUpdateForm(ModelForm):
    ''' car update from '''
    class Meta:
        model = Car
        fields = ('brand', 'name', 'manufacture_year', 'fuel_type', 'transmission_type', 'car_type', 'seats', 'km_driven', 'fare', 'description', 'pickup_address', 'pickup_city', 'pickup_state', 'pickup_country', 'pickup_pincode', 'is_active')

        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Car Name'}),
            'manufacture_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manufacture Year'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Fuel Type'}),
            'transmission_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Transmission Type'}),
            'car_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Car Type'}),
            'seats': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seats'}),
            'km_driven': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'KM Driven'}),
            'fare': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fare'}),
            'description': forms.Textarea(attrs={'class': 'form-control h-100', 'placeholder': 'Description', 'rows': '6'}),
            'pickup_address': forms.Textarea(attrs={'class': 'form-control h-100', 'placeholder': 'Address', 'rows': '3'}),
            'pickup_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'pickup_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pickup_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'pickup_pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CarImagesUpdateForm(ModelForm):
    '''car images update form'''
    class Meta:
        model = CarImage
        fields = ('car', 'car_images')

class RentUpdateForm(ModelForm):
    '''rent updateform for hostuser to update status of bookings'''
    class Meta:
        model = Rent
        fields = ('car', 'pickup_datetime', 'drop_datetime', 'total_fare', 'total_hours', 'booking_status', 'payment_status')
        # fields = ('car', 'booking_status', 'payment_status')

        widgets = {
            'car': forms.HiddenInput(attrs={'class': 'form-control'}),
            'pickup_datetime': forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
            'drop_datetime': forms.HiddenInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
            'total_fare': forms.HiddenInput(attrs={'class': 'form-control'}),
            'total_hours': forms.HiddenInput(attrs={'class': 'form-control'}),
            'booking_status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Booking Status'}),
            'payment_status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Payment Status'}),
        }

class CarHoldTimeForm(ModelForm):
    '''car holdtime forms for hostuser to hold his car for specific time period'''
    class Meta:
        model = CarHoldTime
        fields = ('car', 'start_datetime', 'end_datetime')

        widgets = {
            'car': forms.HiddenInput(),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'DD/MM/YYYY, HH:MM'}),
        }

    # def clean_start_datetime(self):
    #  start_datetime = self.cleaned_data.get('start_datetime')
    #  if start_datetime == "" or start_datetime == None:
    #     raise forms.ValidationError("Select Start Date")
    #  return start_datetime
    
    # def clean_end_datetime(self):
    #  end_datetime = self.cleaned_data.get('end_datetime')
    #  if end_datetime == "" or end_datetime == None:
    #     raise forms.ValidationError("Select End Date")
    #  return end_datetime
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     print("➡ cleaned_data :", cleaned_data)

    #     # print("➡ car :", car)
    #     car = self.cleaned_data["car"]
    #     print("➡ car :", car)
    #     print("➡ car id :", car.id)
    #     startdatetime = self.cleaned_data["start_datetime"]
    #     print("➡ startdatetime :", startdatetime)
    #     enddatetime = self.cleaned_data["end_datetime"]
    #     print("➡ enddatetime :", enddatetime)


    #     rent = Car.objects.filter(id=car.id).filter(car_rent__pickup_datetime__lte=enddatetime,car_rent__drop_datetime__gte=startdatetime)
    #     print("➡ rent :", rent)
        
    #     if rent.exists():
    #         print("aklsjdadslkj")
    #         raise forms.ValidationError("You can not Hold your car on this date range, Car is booked on that dates.")
        

    # def clean_start_datetime(self):
       
    #     car = self.cleaned_data.get("car")
    #     startdatetime = self.cleaned_data.get("start_datetime")
    #     enddatetime = self.cleaned_data.get("end_datetime")

    #     rent = Car.objects.filter(id=car.id).filter(car_rent__pickup_datetime__lte=enddatetime,car_rent__drop_datetime__gte=startdatetime)
        
    #     if rent.exists():
    #         raise ValidationError("You can't Hold your car on this date range, Car is booked on that dates.")
        
    #     return self.start_datetime
    
    # def clean_end_datetime(self):
       
    #     car = self.cleaned_data.get("car")
    #     startdatetime = self.cleaned_data.get("start_datetime")
    #     enddatetime = self.cleaned_data.get("end_datetime")

    #     rent = Car.objects.filter(id=car.id).filter(car_rent__pickup_datetime__lte=enddatetime,car_rent__drop_datetime__gte=startdatetime)
        
    #     if rent.exists():
    #         raise ValidationError("You can't Hold your car on this date range, Car is booked on that dates.")
        
    #     return self.end_datetime
    

