from rest_framework import filters
from django.db.models import Q


class CarListFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """Return filter queryset"""

        # query params
        search = request.GET.get("search")
        id = request.GET.get("id")
        brand = request.GET.get("brand")
        name = request.GET.get("name")
        manufacture_year = request.GET.get("manufacture_year")
        fuel_type = request.GET.get("fuel_type")
        transmission_type = request.GET.get("transmission_type")
        car_type = request.GET.get("car_type")
        registration_no = request.GET.get("registration_no")

        if id:
            queryset = queryset.filter(id=id)
        
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if manufacture_year:
            queryset = queryset.filter(manufacture_year=manufacture_year)

        if fuel_type:
            queryset = queryset.filter(fuel_type__icontains=fuel_type)

        if transmission_type:
            queryset = queryset.filter(transmission_type__icontains=transmission_type)

        if car_type:
            queryset = queryset.filter(car_type__icontains=car_type)

        if registration_no:
            queryset = queryset.filter(registration_no__icontains=registration_no)


        if search:
            queryset = queryset.filter(
                Q(id__icontains=search)
                | Q(brand__icontains=search)
                | Q(name__icontains=search)
                | Q(manufacture_year__icontains=search)
                | Q(fuel_type__icontains=search)
                | Q(transmission_type__icontains=search)
                | Q(car_type__icontains=search)
                | Q(registration_no__icontains=search)
            )

        return queryset

class HoldCarListFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """Return filter queryset"""

        # query params
        search = request.GET.get("search")
        id = request.GET.get("id")
        car = request.GET.get("car")
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        if id:
            queryset = queryset.filter(id=id)
        
        if car:
            queryset = queryset.filter(car=car)

        if start_date:
            queryset = queryset.filter(start_datetime__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(end_datetime__date__lte=end_date)

        if start_date and end_date:
            queryset = queryset.filter(start_datetime__date__gte=start_date, end_datetime__date__lte=end_date)

        if search:
            queryset = queryset.filter(
                Q(id__icontains=search)
                | Q(car__id__icontains=search)
                | Q(car__brand__icontains=search)
                | Q(car__name__icontains=search)
                | Q(start_datetime__date__icontains=search)
                | Q(end_datetime__date__icontains=search)
            )

        return queryset
    

class RentListFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """Return filter queryset"""

        # query params
        search = request.GET.get("search")
        id = request.GET.get("id")
        car = request.GET.get("car")
        user = request.GET.get("user")
        pickup_date = request.GET.get("pickup_date")
        drop_date = request.GET.get("drop_date")
        booking_status = request.GET.get("booking_status")
        payment_status = request.GET.get("payment_status")

        if id:
            queryset = queryset.filter(id=id)
        
        if car:
            queryset = queryset.filter(Q(car__id__icontains=car)
                                       | Q(car__brand__icontains=car)
                                       | Q(car__name__icontains=car))

        if user:
            queryset = queryset.filter(Q(user__username__icontains=user)
                                       | Q(user__first_name__icontains=user)
                                       | Q(user__last_name__icontains=user)
                                       | Q(user__email__icontains=user))            

        if pickup_date:
            queryset = queryset.filter(pickup_datetime__date__gte=pickup_date)

        if drop_date:
            queryset = queryset.filter(drop_datetime__date__lte=drop_date)

        if pickup_date and drop_date:
            queryset = queryset.filter(pickup_datetime__date__gte=pickup_date, drop_datetime__date__lte=drop_date)

        if booking_status:
            queryset = queryset.filter(booking_status__icontains=booking_status)

        if payment_status:
            queryset = queryset.filter(payment_status__icontains=payment_status)

       

        if search:
            queryset = queryset.filter(
                Q(id__icontains=search)
                | Q(car__id__icontains=search)
                | Q(car__brand__icontains=search)
                | Q(car__name__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(pickup_datetime__date__icontains=search)
                | Q(drop_datetime__date__icontains=search)
                | Q(booking_status__icontains=search)
                | Q(payment_status__icontains=search)
            )

        return queryset
    

class RevenueListFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """Return filter queryset"""

        # query params
        search = request.GET.get("search")
        print("➡ search :", search)
        car1 = request.GET.get("car1")
        print("➡ car1 :", car1)
        car2 = request.GET.get("car2")
        print("➡ car2 :", car2)
        car3 = request.GET.get("car3")
        print("➡ car3 :", car3)
        start_date = request.GET.get("start_date")
        print("➡ start_date :", start_date)
        end_date = request.GET.get("end_date")
        print("➡ end_date :", end_date)

        
        # if car1 and car2 and car3:
        #     top_cars_list = [car1, car2, car3]
        #     print("➡ top_cars_list :", top_cars_list)
        #     return top_cars_list

        if car1 and car2 and car3 and start_date and end_date:
            queryset = queryset.filter(drop_datetime__date__gte=start_date, drop_datetime__date__lte=end_date)
            print("➡ queryset :", queryset)
        return queryset

        

       

        # if search:
        #     queryset = queryset.filter(
        #         Q(id__icontains=search)
        #         | Q(car__id__icontains=search)
        #         | Q(car__brand__icontains=search)
        #         | Q(car__name__icontains=search)
        #         | Q(user__username__icontains=search)
        #         | Q(user__first_name__icontains=search)
        #         | Q(user__last_name__icontains=search)
        #         | Q(user__email__icontains=search)
        #         | Q(pickup_datetime__date__icontains=search)
        #         | Q(drop_datetime__date__icontains=search)
        #         | Q(booking_status__icontains=search)
        #         | Q(payment_status__icontains=search)
        #     )

            # return queryset