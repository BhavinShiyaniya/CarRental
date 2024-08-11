from django.contrib import admin
from car.models import Car, CarImage, CarHoldTime, Rent, NotificationGroup, Notification

# Register your models here.

# admin.site.register(Car)
# admin.site.register(CarImage)
# admin.site.register(CarHoldTime)
# admin.site.register(Rent)
# admin.site.register(NotificationGroup)
# admin.site.register(Notification)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'name', 'registration_no', 'manufacture_year')

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'car_images')

@admin.register(CarHoldTime)
class CarHoldTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'start_datetime', 'end_datetime')

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'user', 'pickup_datetime', 'drop_datetime', 'total_hours', 'total_fare', 'booking_status', 'payment_status')

@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'owner', 'group', 'message', 'is_read')