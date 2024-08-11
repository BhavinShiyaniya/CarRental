from django.shortcuts import get_object_or_404
from car.models import Car, CarImage, CarHoldTime, Rent
from car.api.serializers import CarSerializer, CarImageSerializer, CarHoldTimeSerializer, RentSerializer, RevenueSerializer
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import JSONRenderer
from car.api.permissions import IsCarOwner, IsRentCarOwner
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.db.models import Q, F
from django.db.models import Sum, Count
from rest_framework.decorators import action
from car.api.filters import CarListFilter, HoldCarListFilter, RentListFilter, RevenueListFilter
from django.db.models import Prefetch
from rest_framework.generics import ListAPIView

# =======================================
# JWT Authentication
# =======================================
# For generate token JWT = http POST http://127.0.0.1:8000/gettoken/ username="<username>" password="<password>"
# For refresh token JWT = http POST http://127.0.0.1:8000/refreshtoken/ refresh="<refresh token>"
# For verify token JWT = http POST http://127.0.0.1:8000/verifytoken/ token="<access token>"
# http http://127.0.0.1:8000/auth_perm_api/jwt-authentication/ 'Authorization:Bearer <access_token>'
# http -f POST http://127.0.0.1:8000/auth_perm_api/jwt-authentication/ name=Harsh roll=120 city=Surat 'Authorization:Bearer <access_token>'
# http PUT http://127.0.0.1:8000/auth_perm_api/jwt-authentication/6/ name=Lalu roll=120 city=Surat 'Authorization:Bearer <access_token>'
# http DELETE http://127.0.0.1:8000/auth_perm_api/jwt-authentication/6/ 'Authorization:Bearer <access_token>'

# ===========================================

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCarOwner]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['id', '^name', '^brand', 'manufacture_year', 'fuel_type', 'transmission_type', 'car_type', '=registration_no']
    filter_backends = [CarListFilter, OrderingFilter]
    ordering_fields = ['id', 'name', 'brand']
    renderer_classes = [JSONRenderer]
    

    # filter type
    #  '^' Starts-with search
    #  '=' Exact matches
    #  '@' Full-text search (Currently supported Django's PostgreSQL backend.)
    #  '$ Regex search

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user).select_related("owner").annotate(total_bookings=Count("car_rent"))
        return queryset

        # django SubQuery Example

        # from django.db.models import OuterRef, Subquery

        # top_salaries = EmpSalary.objects.filter(
        #     depname=OuterRef('depname')
        # ).order_by('-salary')[:3]
        # result = EmpSalary.objects.filter(
        #     pk__in=Subquery(EmpSalary.objects.filter(
        #     depname=OuterRef('depname')
        # ).order_by('-salary')[:3].values('pk'))
        # ).values('depname', 'empno', 'salary', 'enroll_date')

        # indexing, unique_together


    # Car.objects.filter(owner=self.request.user).select_related("owner__licence")
    # Owner.object.filter(id=34).prefetch_related("user_owner")
    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
    
    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    

    # custom action 
    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated, IsCarOwner], url_path="car_option")
    def car_option(self, request):
        """
        This function will return list of car name or id.
        """
        queryset = self.get_queryset()
        res = queryset.values(Id=F("id"), car_brand=F("brand"), car_name=F("name")).distinct()
        return Response(res)

    
class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRentCarOwner]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'car__id', 'car__brand', 'car__name']
    ordering_fields = ['id', 'car']
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        queryset =  super().get_queryset()
        queryset.filter(car__owner=self.request.user).select_related("car")
        return queryset

    # def list(self, request, *args, **kwargs):
    #     queryset = self.queryset.filter(car__owner=self.request.user).select_related("car")
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
    

class CarHoldTimeViewSet(viewsets.ModelViewSet):
    queryset = CarHoldTime.objects.all()
    serializer_class = CarHoldTimeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRentCarOwner]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['id', 'car__id', 'start_datetime', 'end_datetime']
    filter_backends = [HoldCarListFilter, OrderingFilter]
    ordering_fields = ['id', 'car', 'start_datetime', 'end_datetime']
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        queryset =  super().get_queryset()
        queryset.filter(car__owner=self.request.user).select_related("car")
        return queryset

    # def list(self, request, *args, **kwargs):
    #     queryset = self.queryset.filter(car__owner=self.request.user).select_related("car")
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
    

class RentViewSet(viewsets.ModelViewSet):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRentCarOwner]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['id', 'car__id', 'user__id', 'user__first_name', 'user__last_name', 'user__email', 'user__contact', 'pickup_datetime', 'drop_datetime', 'booking_status', 'payment_status']
    filter_backends = [RentListFilter, OrderingFilter]
    ordering_fields = ['id', 'car', 'user', 'pickup_datetime', 'drop_datetime', 'total_hours', 'total_fare']
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        queryset =  super().get_queryset()
        queryset.filter(car__owner=self.request.user).select_related("car", "user")
        return queryset


    # def list(self, request, *args, **kwargs):
    #     queryset = self.queryset.filter(car__owner=self.request.user).select_related("car", "user")
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class DashboardAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCarOwner]
    

    def get(self, request, format=None):

        userid = self.request.user.id
        usercars = Car.objects.filter(owner_id = userid)
        # car availability
        current_date = datetime.now()
        booked_cars = Car.objects.filter(owner_id = userid).filter((Q(car_rent__pickup_datetime__date__lte=current_date) & Q(car_rent__drop_datetime__date__gte=current_date))).count()
        holded_cars = Car.objects.filter(owner_id = userid).filter((Q(car_carholdtime__start_datetime__date__lte=current_date) & Q(car_carholdtime__end_datetime__date__gte=current_date))).count()
        availableusercars = usercars.count() -(booked_cars + holded_cars)

        bookinglist = Rent.objects.filter(car__owner__id=userid).order_by('-id')

        totalearningsum = bookinglist.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
        totalearning = totalearningsum['total_fare__sum']
        commision_percent = 20
        if totalearning is None:
            net_commision = 0
            net_earning = 0
        else:
            net_commision = (totalearning * commision_percent) / 100
            net_earning = totalearning - net_commision
 
        # total customers count
        totalcustomer = Rent.objects.filter(car__owner__id=userid).values('user__first_name', 'user__last_name', 'user__email', 'user__contact').distinct().count()

        repeat_customers = Rent.objects.filter(car__owner__id=userid).values('user').annotate(booking_count=Count('id')).filter(booking_count__gt=1).count()
        
        if totalcustomer == 0:
            repeat_customers_ratio = 0
        else:
            repeat_customers_ratio = (repeat_customers * 100) / totalcustomer

        top_cars_list = Car.objects.filter(owner_id = userid).annotate(rent_count=Count('car_rent__car'), total_bookings=Count("car_rent")).order_by('-rent_count')[:5]


        new_customers_month = Rent.objects.filter(car__owner__id = userid).values('user').annotate(booking_count=Count('id')).filter(booking_count=1,created_at__month=current_date.month, created_at__year=current_date.year).distinct().count()
        
        # bookings increase / decrease

        last_month = current_date - timedelta(days=current_date.day)
        current_month_bookings = Rent.objects.filter(pickup_datetime__month=current_date.month, pickup_datetime__year=current_date.year).aggregate(current_month_bookings=Count('id'))['current_month_bookings']

        last_month_bookings = Rent.objects.filter(pickup_datetime__month=last_month.month, pickup_datetime__year=last_month.year).aggregate(last_month_bookings=Count('id'))['last_month_bookings']

        if last_month_bookings != 0:
            percentage_change = ((current_month_bookings - last_month_bookings) / last_month_bookings) * 100
        else:
            percentage_change = 0
        
        # end of booking increase/decrease

        top_car_serializer = CarSerializer(top_cars_list, many=True)
        bookings_serializer = RentSerializer(bookinglist, many=True)

        res = {
            'total_cars': usercars.count(),
            'total_available_cars': availableusercars,
            'cars_on_rent': booked_cars,
            'cars_on_hold': holded_cars,
            'total_earning': totalearning,
            'net_earning': net_earning,
            'net_commision': net_commision,
            'totalcustomer': totalcustomer,
            'total_bookings': bookinglist.count(),
            'current_month_bookings': current_month_bookings,
            'last_month_bookings': last_month_bookings,
            'booking_percentage_change': percentage_change,
            'repeat_customers_ratio': repeat_customers_ratio,
            'repeat_customers': repeat_customers,
            'new_customers_month': new_customers_month,
            'top_cars_list': top_car_serializer.data,
            'bookinglist': bookings_serializer.data,
        }

        return Response(res)
    

    # http://127.0.0.1:8000/hostuser/revenue-compare-ajax/?start_date=&end_date=&car1=1&car2=2&car3=4

class RevenueApi(viewsets.ModelViewSet):
    queryset = Rent.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCarOwner]
    filter_backends = [RevenueListFilter]


    def list(self, request, *args, **kwargs):

        usercars = Car.objects.filter(owner_id = self.request.user.id)
        car_list = request.data.get("car_list")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if car_list:
            top_cars_list = Car.objects.filter(id__in = car_list).annotate(rent_count=Count('car_rent__car'))
        else:
            top_cars_list = Car.objects.filter(owner_id = self.request.user.id).annotate(rent_count=Count('car_rent__car')).order_by('-rent_count')[:3]

        revenue = []
        for car in top_cars_list:
            if start_date and end_date:
                booking = self.queryset.filter(car__id=car.id).filter(drop_datetime__date__gte=start_date, drop_datetime__date__lte=end_date)
            else:
                booking = self.queryset.filter(car__id=car.id)
            earningsum = booking.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
            earning = earningsum['total_fare__sum']
            commision_percent = 20
            commision = ((earning or 0) * commision_percent) / 100
            total_net_earning = (earning or 0) - commision

            earning_dict = {'car':car.id, 'totalearning':earning or 0, 'net_commision':commision, 'net_earning':total_net_earning, 'booking':booking.count()}
            revenue.append(earning_dict)

        top_cars_list_serializer = RevenueSerializer(top_cars_list, many=True)
        usercars_serializer = RevenueSerializer(usercars, many=True)
        
        res = {
            "revenue": revenue,
            "top_cars_list": top_cars_list_serializer.data,
            "usercars": usercars_serializer.data,
        }

        return Response(res)
    
    # custom action 
    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated, IsCarOwner], url_path="car_option")
    def car_option(self, request):
        """
        This function will return list of car name or id.
        """
        queryset = Car.objects.filter(owner=self.request.user)
        res = queryset.values(Id=F("id"), car_brand=F("brand"), car_name=F("name")).distinct()

        return Response(res)