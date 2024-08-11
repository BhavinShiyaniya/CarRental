from django.db import models
from base.models import BaseModel
from user.models import User
from django.urls import reverse_lazy

# Create your models here.


class Car(BaseModel):
    '''Car model'''
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_owner')
    brand = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    manufacture_year = models.PositiveIntegerField()
    FUEL_TYPES = (
        ("PETROL", "Petrol"),
        ("DIESEL", "Diesel"),
        ("CNG", "CNG"),
        ("EV", "Electric"),
    )
    fuel_type = models.CharField(max_length=256, choices=FUEL_TYPES, default="PETROL")
    TRANSMISSION_TYPES = (
        ("MANUAL", "Manual"),
        ("AUTOMATIC", "Automatic"),
    )
    transmission_type = models.CharField(max_length=256, choices=TRANSMISSION_TYPES, default="MANUAL")
    CAR_TYPES = (
        ("SEDAN", "Sedan"),
        ("HATCHBACK", "Hatchback"),
        ("SUV","SUV"),
        ("COUPE", "Coupe"),
    )
    car_type = models.CharField(max_length=256, choices=CAR_TYPES, default="SEDAN")
    seats = models.PositiveIntegerField()
    registration_no = models.CharField(max_length=10, unique=True)
    km_driven = models.PositiveBigIntegerField()
    fare = models.PositiveIntegerField()
    description = models.TextField(max_length=1000)
    pickup_address = models.TextField()
    pickup_city = models.CharField(max_length=256)
    pickup_state = models.CharField(max_length=256)
    pickup_country = models.CharField(max_length=256)
    pickup_pincode = models.CharField(max_length=256)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def get_detail_url(self):
        return f"/hostuser/hostcardetail/{self.pk}"
    
    def get_update_url(self):
        return f"/hostuser/carupdate/{self.pk}"
    
    def get_delete_url(self):
        return f"/hostuser/cardelete/{self.pk}"


class CarImage(BaseModel):
    '''car images model'''
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_image_set') # oldname = car_name
    car_images = models.ImageField(upload_to='car_images')

    def __str__(self):
        return self.car.name
    

class CarHoldTime(BaseModel):
    '''car hold time model for hostuser'''
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_carholdtime')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    # def __str__(self):
    #     return self.car.name


class Rent(BaseModel):
    '''rent model for bookings data'''
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car_rent") # oldname = car_name
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user') # oldname = user_name
    pickup_datetime = models.DateTimeField()
    # pickup_time = models.TimeField()
    # pickup_place = models.CharField(max_length=256)
    drop_datetime = models.DateTimeField()
    # drop_time = models.TimeField()
    total_hours = models.PositiveIntegerField(default=None)
    total_fare = models.FloatField()
    BOOKING_STATUS = (
        ("CONFIRMED", "Confirmed"),
        ("PICKEDUP", "Pickedup"),
        ("DROPPED", "Dropped"),
        ("CANCELLED", "Cancelled"),
    )
    booking_status = models.CharField(max_length=256, choices=BOOKING_STATUS, default="CONFIRMED")
    PAYMENT_STATUS = (
        ("COMPLETED", "Completed"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    )
    payment_status = models.CharField(max_length=256, choices=PAYMENT_STATUS, default="PENDING")

    # def __str__(self):
    #     return self.car.car + " " + self.user


class NotificationGroup(BaseModel):
    '''create notification group'''
    name = models.CharField(max_length=100)

class Notification(BaseModel):
    '''save notification'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rent')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_car')
    group = models.ForeignKey(NotificationGroup, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)