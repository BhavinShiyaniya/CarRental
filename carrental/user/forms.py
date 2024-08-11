from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db import transaction
from user.models import User
from car.models import Car, CarImage

class UserRegisterForm(UserCreationForm):
    '''form for create a new user'''
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'contact', 'password1', 'password2', 'profile_image')

        widgets = {
            'contact': forms.TextInput(attrs={'minlength':'10',}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['profile_image'].required = False


    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_hostuser = False
        user.save()
        return user
    


class CarRegisterForm(ModelForm):
    '''form for create a new car from user'''
    class Meta:
        model = Car
        fields = ('brand', 'name', 'manufacture_year', 'fuel_type', 'transmission_type', 'car_type', 'seats', 'registration_no', 'km_driven', 'fare', 'description', 'pickup_address', 'pickup_city', 'pickup_state', 'pickup_country', 'pickup_pincode', 'is_active')

        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    # @transaction.atomic
    # def save(self):
    #     car = super().save(commit=False)
    #     car.owner = self.request.user
    #     car.is_available = True
    #     car.save()
    #     return car


class CarImagesForm(ModelForm):
    '''form for create images for car'''
    class Meta:
        model = CarImage
        fields = ('car_images',)

    
class UserProfileUpdateForm(ModelForm):
    '''form for update user profile'''
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'contact', 'profile_image')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', "accept": "image/*"}),
        }


class UserProfileImageUpdateForm(ModelForm):
    '''form for update user profile'''
    class Meta:
        model = User
        fields = ('profile_image',)

        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control', "accept": "image/*", "required":"true"}),
        }


class PasswordChangingForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password', 'type': 'password'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password', 'type': 'password'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'type': 'password'})

