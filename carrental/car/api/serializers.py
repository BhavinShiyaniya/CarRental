from car.models import Car, CarImage, CarHoldTime, Rent
from rest_framework import serializers

class CarSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    # owner_name = serializers.SerializerMethodField()
    owner_name = serializers.ReadOnlyField()
    # total_bookings = serializers.SerializerMethodField()
    total_bookings = serializers.ReadOnlyField()
    class Meta:
        model = Car
        fields = ['id', 'total_bookings', 'owner', 'owner_name', 'brand', 'name', 'manufacture_year', 'fuel_type', 'transmission_type', 'car_type', 'seats', 'registration_no', 'km_driven', 'fare', 'description', 'pickup_address', 'pickup_city', 'pickup_state', 'pickup_country', 'pickup_pincode', 'is_available', 'is_active']

        
    def get_owner_name(self, obj: Car):
        return obj.owner.first_name
    
    def get_total_bookings(self, obj: Car):
        print("obj:", obj.__dict__)
        return obj.total_bookings
    
class CarImageSerializer(serializers.ModelSerializer):
    # car_brand = serializers.SerializerMethodField()
    # car_name = serializers.SerializerMethodField()
    car_brand = serializers.ReadOnlyField()
    car_name = serializers.ReadOnlyField()
    class Meta:
        model = CarImage
        fields = ['id', 'car', 'car_brand', 'car_name', 'car_images']

    def get_car_brand(self, obj: CarImage):
        return obj.car.brand
    
    def get_car_name(self, obj: CarImage):
        return obj.car.name


class CarHoldTimeSerializer(serializers.ModelSerializer):
    # car_brand = serializers.SerializerMethodField()
    # car_name = serializers.SerializerMethodField()
    car_brand = serializers.ReadOnlyField()
    car_name = serializers.ReadOnlyField()
    class Meta:
        model = CarHoldTime
        fields = ['id', 'car', 'car_brand', 'car_name', 'start_datetime', 'end_datetime']
    
    def get_car_brand(self, obj: CarHoldTime):
        return obj.car.brand
    
    def get_car_name(self, obj: CarHoldTime):
        return obj.car.name


class RentSerializer(serializers.ModelSerializer):
    # car_brand = serializers.SerializerMethodField()
    # car_name = serializers.SerializerMethodField()
    # user_first_name = serializers.SerializerMethodField()
    # user_last_name = serializers.SerializerMethodField()
    # user_email = serializers.SerializerMethodField()
    car_brand = serializers.ReadOnlyField()
    car_name = serializers.ReadOnlyField()
    user_first_name = serializers.ReadOnlyField()
    user_last_name = serializers.ReadOnlyField()
    user_email = serializers.ReadOnlyField()
    class Meta:
        model = Rent
        fields = ['id', 'car', 'car_brand', 'car_name', 'user', 'user_first_name', 'user_last_name', 'user_email', 'pickup_datetime', 'drop_datetime', 'total_hours', 'total_fare', 'booking_status', 'payment_status']

    def get_car_brand(self, obj: Rent):
        return obj.car.brand
    
    def get_car_name(self, obj: Rent):
        return obj.car.name
    
    def get_user_first_name(self, obj: Rent):
        return obj.user.first_name

    def get_user_last_name(self, obj: Rent):
        return obj.user.last_name
    
    def get_user_email(self, obj: Rent):
        return obj.user.email


class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'brand', 'name', 'manufacture_year', 'fuel_type', 'transmission_type', 'car_type', 'seats', 'registration_no', 'km_driven', 'fare', 'description', 'pickup_address', 'pickup_city', 'pickup_state', 'pickup_country', 'pickup_pincode', 'is_available', 'is_active']
