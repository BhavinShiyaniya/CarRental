from typing import Any
from django.forms import FloatField
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, View, TemplateView
from user.models import User
from car.models import Car, CarImage, Rent, CarHoldTime, NotificationGroup, Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from user.forms import UserProfileUpdateForm, UserProfileImageUpdateForm, PasswordChangingForm
from hostuser.forms import CarUpdateForm, CarImagesUpdateForm, RentUpdateForm, CarHoldTimeForm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.paginator import Paginator
from django_datatables_too.mixins import DataTableMixin
from django.db.models import Sum, Count
from hostuser.filters import BookingsListFilter
from django.template.loader import render_to_string
from car.tasks import send_receipt
from base.permissions import OwnerLoginRequiredMixin, OwnerRequiredMixin, BookingOwnerRequiredMixin, ImageOwnerRequiredMixin, HoldOwnerRequiredMixin, ProfileOwnerRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib import messages

# Create your views here.

def dashboard(request):
    '''for testing dashboard template'''
    return render(request, 'hostuser/dashboard.html')

def hostcardetail(request):
    '''for testing host car detail template'''
    return render(request, 'hostuser/host_car_detail.html')



class DashboardView(OwnerLoginRequiredMixin, TemplateView):
    '''Dashboard view for show car and booking data to owner'''
    model = Car
    template_name = "hostuser/dashboard.html"
    # context_object_name = 'carlist'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userid = self.request.user.id
        usercars = Car.objects.filter(owner_id = userid)
        # availableusercars = Car.objects.filter(owner_id = userid).filter(Q(is_available=True))
        # car availability
        current_date = datetime.now()
        booked_cars = Car.objects.filter(owner_id = userid).filter((Q(car_rent__pickup_datetime__date__lte=current_date) & Q(car_rent__drop_datetime__date__gte=current_date))).count()
        holded_cars = Car.objects.filter(owner_id = userid).filter((Q(car_carholdtime__start_datetime__date__lte=current_date) & Q(car_carholdtime__end_datetime__date__gte=current_date))).count()
        availableusercars = usercars.count() -(booked_cars + holded_cars)

        bookinglist = Rent.objects.filter(car__owner__id=userid).order_by('-id')

        totalearningsum = bookinglist.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
        totalearning = totalearningsum['total_fare__sum']
        commision_percent = 20
        net_commision = (totalearning * commision_percent) / 100
        net_earning = totalearning - net_commision

        # total customers count
        totalcustomer = Rent.objects.filter(car__owner__id=userid).values('user__first_name', 'user__last_name', 'user__email', 'user__contact').distinct().count()

        repeat_customers = Rent.objects.filter(car__owner__id=userid).values('user').annotate(booking_count=Count('id')).filter(booking_count__gt=1).count()
        repeat_customers_ratio = (repeat_customers * 100) / totalcustomer

        top_cars_list = Car.objects.filter(owner_id = userid).annotate(rent_count=Count('car_rent__car')).order_by('-rent_count')[:5]


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


        context["usercars"] = usercars
        context["availableusercars"] = availableusercars
        context["booked_cars"] = booked_cars
        context["holded_cars"] = holded_cars
        context["totalearning"] = totalearning
        context["net_earning"] = net_earning
        context["net_commision"] = net_commision
        context["totalcustomer"] = totalcustomer
        context["bookinglist"] = bookinglist
        context["top_cars_list"] = top_cars_list
        context["repeat_customers_ratio"] = repeat_customers_ratio
        context["repeat_customers"] = repeat_customers
        context["new_customers_month"] = new_customers_month
        context["total_bookings"] = bookinglist.count()
        context["current_month_bookings"] = current_month_bookings
        context["last_month_bookings"] = last_month_bookings
        context["percentage_change"] = percentage_change
        context["booked_cars"] = booked_cars
        context["holded_cars"] = holded_cars

        return context

class AjaxRevenueChartDataView(OwnerLoginRequiredMixin, View):
    '''ajax view for send data based on date seleted to revenue chart on dashboard'''

    def get(self, request):

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        this_month = self.request.GET.get("this_month")
        three_month = self.request.GET.get("three_month")

        bookinglist = Rent.objects.filter(car__owner__id=self.request.user.id).order_by('-id')

        if three_month:
            print("three month")
            end_date = datetime.now().date()
            print("➡ current_date :", end_date)
            start_date = end_date - relativedelta(months=3)
            print("➡ start_date_three_month :", start_date)
        elif this_month:
            print("this month")
            end_date = datetime.now().date()
            print("➡ current_date :", end_date)
            start_date = end_date.replace(day=1) - timedelta(days=0)
            print("➡ start_date_three_month :", start_date)


            
        totalearningsum = bookinglist.filter(drop_datetime__date__gte=start_date, drop_datetime__date__lte=end_date).values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
        totalearning = totalearningsum['total_fare__sum']
        if totalearning:
            commision_percent = 20
            net_commision = (totalearning * commision_percent) / 100
            net_earning = totalearning - net_commision

            context = {'totalearning':totalearning, 'net_commision':net_commision, 'net_earning':net_earning}
            return JsonResponse(context)

        return JsonResponse({"totalearning": 0, 'net_commision':0, 'net_earning':0})
    
    
# Start of Car CRUD Views
    
    
class CarListView(OwnerLoginRequiredMixin, ListView):
    '''carlist view to display list of all car's of perticular owner'''
    model = Car
    template_name = 'hostuser/car_list.html'
    # context_object_name = 'car'

    def get_queryset(self):
        return Car.objects.filter(owner_id = self.request.user.id).order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usercars = Car.objects.filter(owner_id = self.request.user.id).order_by('-id')

        # paginator
        # paginator = Paginator(usercars, 10)
        # page_number = self.request.GET.get('page')
        # usercarsFinal = paginator.get_page(page_number)
        # totalPages = usercarsFinal.paginator.num_pages

        # context = {'usercars':usercarsFinal, 'lastpage':totalPages, 'totalPagelist': [n+1 for n in range(totalPages)]}

        # context["usercars"] = usercarsFinal
        # context["lastpage"] = totalPages
        # context["totalPagelist"] = [n+1 for n in range(totalPages)]

        return context
      
    
class CarListDataTablesAjaxPagination(OwnerLoginRequiredMixin, DataTableMixin, View):
    model = Car
    queryset = Car.objects.all().order_by('-id')

    # def _get_delete_form(self, obj):
    #     """Get Delete Form"""
    #     csrf = self.request.POST.get("csrfmiddlewaretoken")
    #     return f'<form method="POST"><input type="hidden" id="csrf_token" value="{csrf}" /><input type="hidden" id="car" name="car" value="{obj.id}" /><button type="submit" value="{obj.id}"class="btn btn-danger me-md-2 confirmdeletebtn" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-original-title="Delete"><i class="fa fa-trash"></i></button></form>'


    def _get_actions(self, obj):
        """Get action buttons w/links."""
        return f'<a href="{obj.get_detail_url()}" title="Detail" class="btn btn-primary btn-xs"><i class="fas fa-arrow-alt-circle-right"></i></a> <a href="{obj.get_update_url()}" title="Edit" class="btn btn-success btn-xs"><i class="fa fa-edit"></i></a> <label data-url="{obj.get_delete_url()}" data-title="{obj.id}" title="Delete" href="{obj.get_delete_url()}" class="btn btn-danger confirmdeletebtn" data-id="{obj.id}"><i class="fa fa-trash"></i></label>'
    

    def filter_queryset(self, qs):
        """Return the list of items for this view."""
        # If a search term, filter the query
        print("search: ", self.search)
        qs = qs.filter(owner_id = self.request.user.id).order_by('-id')
        start = int(self.request.GET.get("start"))
        length = int(self.request.GET.get("length"))

        totalcarsobj = Car.objects.filter(owner_id = self.request.user.id).count()
        print("➡ totalcarsobj :", totalcarsobj)
        # qs = Car.objects.filter(owner_id = self.request.user.id)
        # print("➡ qs :", qs)


        if self.search:
            qs =  qs.filter(
                Q(id__icontains=self.search) |
                Q(brand__icontains=self.search) |
                Q(name__icontains=self.search) |
                Q(fuel_type__icontains=self.search) |
                Q(registration_no__icontains=self.search) |
                Q(is_available__icontains=self.search) 
            )
            try:
                qs = qs[int(start):int(start)+int(length)]
            except:
                pass
    
            return qs
        
        try:
            qs = qs[int(start):int(start)+int(length)]
        except:
            pass
        return qs
        
    
    def get_status(self, obj):
        if obj.is_available == True:
            return f'<td><span class="badge bg-success">Available</span></td>'
        elif obj.is_available == False:
            return f'<td><span class="badge bg-danger">Booked</span></td>'
        elif obj.is_active == False:
            return f'<td><span class="badge bg-warning">On Hold</span></td>'

    def prepare_results(self, car):
        # Create row data for datatables
        # data = []
        # for o in qs:
            # data.append({
            #     'id': o.id,
            #     'brand': o.brand,
            #     'name': o.name,
            #     'fuel_type': o.fuel_type,
            #     'registration_no': o.registration_no,
            #     # 'is_active': o.is_active,
            #     'is_active': self._get_status(o),
            #     'actions': self._get_actions(o)
            # })
        return {
            'id': car.id,
            'car': car.brand + ' ' + car.name,
            'fuel_type': car.fuel_type,
            'registration_no': car.registration_no,
            'is_active': self.get_status(car),
            'actions': self._get_actions(car)
        }

        # return data

    def get(self, request, *args, **kwargs):
        # context_data = self.get_context_data(request)
        qs = self.queryset.filter(owner_id = self.request.user.id).order_by('-id')
        total_records = qs.count()
        qs = self.filter_queryset(self.queryset)
        print("➡ qsfilter :", qs)
        filterobject = qs.count()
        print("➡ filterobject :", filterobject)
        data = [self.prepare_results(car) for car in qs]
        print("➡ data :", data)
        dict = {'data': data, 'recordsFiltered':total_records}
        print("➡ dict :", dict)

        print("➡ qs :", qs.count())
        
        # qs = qs[start: start+length]
        # return qs
        return JsonResponse(dict)
    
        # return JsonResponse(context_data)


class HostCarDetailView(OwnerRequiredMixin, DetailView):
    '''cardetail view for owner'''
    model=Car
    context_object_name = 'car'
    template_name = 'hostuser/host_car_detail.html'

    def get_context_data(self, **kwargs):
        context = super(HostCarDetailView, self).get_context_data(**kwargs)
        context['form'] = CarHoldTimeForm()
        return context
    
    
class CarUpdateView(OwnerRequiredMixin, UpdateView):
    '''car update view for update car by owner only'''
    model = Car
    template_name = 'hostuser/car_update.html'
    form_class = CarUpdateForm
    context_object_name = 'car'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["carimages"] = CarImagesUpdateForm
        return context
    
    def form_valid(self, form):
        car = form.save(commit=False)
        car.save()
        car_images = self.request.FILES.getlist("car_images")
        for img in car_images:
            CarImage.objects.create(car=car, car_images=img)
        messages.success(self.request, "Car Updated successfully!")
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy('hostuser:hostcardetail', kwargs={'pk': self.kwargs['pk']})
    
class SingleCarImageDeleteView(ImageOwnerRequiredMixin, View):
    '''delete view for single car image from update car view'''
    model = CarImage

    def post(self, *args, **kwargs):
        image_id = self.request.POST.get('image_id')
        image = CarImage.objects.get(id=image_id)
        car = CarImage.objects.get(id=image_id).car
        image.delete()
        messages.success(self.request, "Car Image deleted successfully!")
        return HttpResponseRedirect(reverse_lazy('hostuser:carupdate', kwargs={'pk':car.id})) 
    

    
class CarDeleteView(OwnerRequiredMixin, DeleteView):
    '''car delete view for owner'''
    model = Car
    # template_name = 'hostuser/confirm_delete_modal.html'
    template_name = 'hostuser/car_list.html'
    success_url = reverse_lazy("hostuser:carlist")
    login_url = '/account/login'
    redirect_field_name = reverse_lazy("hostuser:carlist")

    
# End of Car CRUD Views



# Start of Bookings Views for CRUD

class HostBookingListView(OwnerLoginRequiredMixin, ListView):
    '''booking list for owner for his cars'''
    model = Rent
    template_name = 'hostuser/host_booking_list.html'
    context_object_name = 'bookinglist'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:hostbookinglist')


    def get_queryset(self):
        return Rent.objects.filter(car__owner__id=self.request.user.id).order_by('-id')
    
    # def get(self, request, *args, **kwargs):
    #     bookinglist = self.get_queryset()
    #     print("➡ bookinglist :", bookinglist)
       
    #     myFilter = BookingsListFilter(request.GET, queryset=bookinglist)
    #     bookinglist = myFilter.qs
    #     print("➡ bookinglist :", bookinglist)

    #     return render(request, self.template_name, {'bookinglist': bookinglist, 'myFilter': myFilter})
    
    
    # def get(self, request, *args, **kwargs):
    #     bookinglist = Rent.objects.filter(car__owner__id=self.request.user.id)

    #     start_date = self.request.GET.get("start_date")
    #     end_date = self.request.GET.get("end_date")

    #     if start_date == "" and end_date == "":
    #         return render(request, self.template_name, {'bookinglist':self.get_queryset()})
    #     else:
    #         bookinglist = bookinglist.filter(pickup_datetime__gte=start_date, pickup_datetime__lte=end_date)
    #         return render(request, self.template_name, {'bookinglist':bookinglist})

class HostBookingListDataTablesAjaxPagination(OwnerLoginRequiredMixin, DataTableMixin, View):
    model = Rent
    queryset = Rent.objects.all().order_by('-id')

    def _get_actions(self, obj):
        """Get action buttons w/links."""
        detail_url = reverse_lazy("hostuser:hostbookingdetail", kwargs={"pk":obj.id})
        return f'<a href="{detail_url}" class="btn btn-primary" data-bs-toggle="tooltip" data-bs-placement="left" data-bs-original-title="View"><i class="fas fa-arrow-alt-circle-right"></i></a>'

    def filter_queryset(self, qs):
        """Return the list of items for this view."""
        # If a search term, filter the query
        qs = qs.filter(car__owner__id=self.request.user.id).order_by('-id')
        start = int(self.request.GET.get("start"))
        length = int(self.request.GET.get("length"))

        if self.search:
            qs =  qs.filter(
                Q(id__icontains=self.search) |
                Q(user__first_name__icontains=self.search) |
                Q(user__last_name__icontains=self.search) |
                Q(car__brand__icontains=self.search) |
                Q(car__name__icontains=self.search) |
                Q(pickup_datetime__icontains=self.search) |
                Q(car__registration_no__icontains=self.search) |
                Q(booking_status__icontains=self.search) 
            )
            try:
                qs = qs[int(start):int(start)+int(length)]
            except:
                pass
    
            return qs
        
        try:
            qs = qs[int(start):int(start)+int(length)]
        except:
            pass

        return qs
    
    def get_status(self, obj):
        if obj.booking_status == "CONFIRMED":
            return f'<td><span class="badge bg-primary">{obj.booking_status }</span></td>'
        elif obj.booking_status == "PICKEDUP":
            return f'<td><span class="badge bg-warning">{ obj.booking_status }</span></td>'
        elif obj.booking_status == "DROPPED":
            return f'<td><span class="badge bg-success">{ obj.booking_status }</span></td>'
        elif obj.booking_status == "CANCELLED":
            return f'<td><span class="badge bg-danger">{ obj.booking_status }</span></td>'

    def prepare_results(self, booking):
        # Create row data for datatables
        
        return {
            'id': booking.id,
            'user': booking.user.first_name + ' ' + booking.user.last_name,
            'car': booking.car.brand + ' ' + booking.car.name,
            'pickup_datetime': f'{booking.pickup_datetime.date()} {booking.pickup_datetime.time()}',
            'registration_no': booking.car.registration_no,
            'booking_status': self.get_status(booking),
            'actions': self._get_actions(booking)
        }

    def get(self, request, *args, **kwargs):
        qs = self.queryset.filter(car__owner__id=self.request.user.id).order_by('-id')
        total_records = qs.count()
        qs = self.filter_queryset(self.queryset)
        filterobject = qs.count()
        data = [self.prepare_results(booking) for booking in qs]
        dict = {'data': data, 'recordsFiltered':total_records}

        return JsonResponse(dict)

    
class HostBookingDetailView(BookingOwnerRequiredMixin, DetailView):
    '''booking detail view for owner for perticular booking'''
    model = Rent
    template_name = 'hostuser/host_booking_detail.html'
    context_object_name = 'booking'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:hostbookinglist')

    def get_context_data(self, **kwargs):
        context = super(HostBookingDetailView, self).get_context_data(**kwargs)
        rent = self.object
        initial_dict = {
            'car':rent.car_id, 
            'pickup_datetime':rent.pickup_datetime, 
            'drop_datetime':rent.drop_datetime, 
            'total_fare':rent.total_fare, 
            'total_hours':rent.total_hours, 
            'booking_status':rent.booking_status, 
            'payment_status':rent.payment_status
        }
        context["form"] = RentUpdateForm(initial=initial_dict)
        return context
    


class HostBookingUpdateView(BookingOwnerRequiredMixin, UpdateView):
    '''booking update view for update status of booking'''
    model = Rent
    template_name = 'hostuser/host_booking_detail.html'
    # template_name = 'hostuser/booking_update.html'
    form_class = RentUpdateForm
    context_object_name = 'booking'
    # success_url = reverse_lazy('hostuser:hostbookinglist')
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:hostbookinglist')

    def form_valid(self, form):
        rent = form.save(commit=False)
        # rent.user = self.request.user
        # car = self.request.POST.get("car")
        car = form.cleaned_data['car']
        
        car = Car.objects.get(pk=car.id)

        booking_status = form.cleaned_data["booking_status"]

        pickup_datetime = form.cleaned_data['pickup_datetime']
        drop_datetime = form.cleaned_data['drop_datetime']  
        
        utc_dt_now = datetime.now(timezone.utc)

        local_dt_now = utc_dt_now + timedelta(hours=5,minutes=30)

        dt_difference = local_dt_now - pickup_datetime
        
        days, seconds = dt_difference.days, dt_difference.seconds
        hours = days*24 + seconds // 3600
        minutes = (seconds % 3600) // 60


        # time = f"{dt_difference}"
        # hour = int(time[0:2])
        # print("hour :", hour)
        # minute = int(time[3:5])
        # print("minute :", minute)
        # min_to_hour = minute/60
        # print("min_to_hour :", min_to_hour)
        # t_hours = hour + min_to_hour
        # print("t_hours :", t_hours)
        # updated_total_hours = math.ceil(t_hours)
        # print("updated_total_hours :", updated_total_hours)

        fare = car.fare

        updated_fare = hours * fare

        if booking_status == "DROPPED":
            car.is_available = True
            rent.drop_datetime = local_dt_now
            rent.total_fare = updated_fare
            rent.total_hours = hours
            rent.booking_status = "DROPPED"
            rent.payment_status = "COMPLETED"
            rent.save()

            # for celery send receipt mail

            carowneremail = list(Car.objects.filter(id=car.id).values_list('owner__email', flat=True))[0]
            user_email = list(Rent.objects.filter(id=rent.id).values_list('user__email', flat=True))[0]
            to_email = [user_email, carowneremail]
            # rent_obj = Rent.objects.filter(id=rent.id)
            # context = serializers.serialize('json', rent_obj)
            # print("➡ context :", context)
            rent_id=rent.id
            send_receipt.delay(to_email, rent_id)
        else:
            car.is_available = "False"

        car.save()
        rent.save()
        messages.success(self.request, "Booking Status Updated successfully!")
        return HttpResponseRedirect(self.get_success_url())
    
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy('hostuser:hostbookingdetail', kwargs={'pk': self.kwargs['pk']})

# End of Bookings Views for CRUD


# Start of Car HoldTime Views for CRUD

class CarHoldTimeCreateView(OwnerLoginRequiredMixin, CreateView):
    '''create view for car holdtime from owner'''
    model = CarHoldTime
    template_name = 'hostuser/host_car_detail.html'
    # template_name = 'hostuser/car_hold_createform.html'
    form_class = CarHoldTimeForm
    context_object_name = 'car'
    success_url = reverse_lazy("hostuser:holdcarlist")
    login_url = '/account/login'
    redirect_field_name = reverse_lazy("hostuser:holdcarlist")

    def form_valid(self, form):
        carhold = form.save(commit=False)
        car = form.cleaned_data["car"]
        
        # check date is available or not
        startdatetime = form.cleaned_data['start_datetime']
        enddatetime = form.cleaned_data['end_datetime']
            
        rent = Car.objects.filter(id=car.id).filter((Q(car_rent__pickup_datetime__lte=enddatetime) & Q(car_rent__drop_datetime__gte=startdatetime)) | (Q(car_carholdtime__start_datetime__lte=enddatetime) & Q(car_carholdtime__end_datetime__gte=startdatetime))).exists()

        if rent:
            raise ValidationError("You can't Hold your car on this date range, Car is booked on that dates.")

        car = Car.objects.get(pk=car.id)
        car.is_active = "False"
        car.save()
        carhold.save()

        messages.success(self.request, "Car Hold Time Created successfully!")
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response


class AjaxCarAvailabilityCheckView(LoginRequiredMixin, View):
    '''ajax view for checking car availability when owner is put his car on hold'''

    def get(self, request):
        car_id = self.request.GET.get("car_id")
        start_time = self.request.GET.get("start_datetime")
        end_time = self.request.GET.get("end_datetime")

        car_obj = Car.objects.filter(id=car_id).filter((Q(car_rent__pickup_datetime__lte=end_time) & Q(car_rent__drop_datetime__gte=start_time)) | (Q(car_carholdtime__start_datetime__lte=end_time) & Q(car_carholdtime__end_datetime__gte=start_time)))

        if car_obj.count()>0:
            return JsonResponse({"message": "You can't Hold your car on this date range, Car is booked or already hold on that dates.", "status":"401"})
        else:
            return JsonResponse({"message": "Available"})
    

class HoldCarListView(OwnerLoginRequiredMixin, ListView):
    '''list view for car holdtime from owner'''
    model = CarHoldTime
    template_name = 'hostuser/hold_car_list.html'
    context_object_name = 'holdusercars'

    def get_queryset(self):
        return CarHoldTime.objects.filter(car__owner_id = self.request.user.id).order_by('-id')
    

class HoldCarListDataTablesAjaxPagination(OwnerLoginRequiredMixin, DataTableMixin, View):
    model = CarHoldTime
    queryset = CarHoldTime.objects.all().order_by('-id')

    def _get_actions(self, obj):
        """Get action buttons w/links."""
        update_url = reverse_lazy("hostuser:carholdupdate", kwargs={"pk":obj.id})
        delete_url = reverse_lazy("hostuser:carholddelete", kwargs={"pk":obj.id})
        return f'<a href="{update_url}" class="btn btn-success" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-original-title="Update"><i class="fa fa-edit"></i></a> <label data-url="{delete_url}" "data-title="{obj.id}" title="Delete" href="{delete_url}" class=" btn btn-danger confirmdeletebtn" data-id="{obj.id}"><i class="fa fa-trash"></i></label>'

    def filter_queryset(self, qs):
        """Return the list of items for this view."""
        # If a search term, filter the query
        qs = qs.filter(car__owner_id = self.request.user.id).order_by('-id')
        start = int(self.request.GET.get("start"))
        length = int(self.request.GET.get("length"))

        if self.search:
            qs =  qs.filter(
                Q(id__icontains=self.search) |
                Q(car__brand__icontains=self.search) |
                Q(car__name__icontains=self.search) |
                Q(start_datetime__icontains=self.search) |
                Q(end_datetime__icontains=self.search) |
                Q(car__registration_no__icontains=self.search) 
            )
            try:
                qs = qs[int(start):int(start)+int(length)]
            except:
                pass
    
            return qs
        
        try:
            qs = qs[int(start):int(start)+int(length)]
        except:
            pass

        return qs

    def prepare_results(self, car):
        # Create row data for datatables
        
        return {
            'id': car.id,
            'car': f'{car.car.brand} {car.car.name}',
            'registration_no': car.car.registration_no,
            'start_datetime': f'{car.start_datetime.date()} {car.start_datetime.time()}',
            'end_datetime': f'{car.end_datetime.date()} {car.end_datetime.time()}',
            'actions': self._get_actions(car)
        }

    def get(self, request, *args, **kwargs):
        qs = self.queryset.filter(car__owner_id = self.request.user.id).order_by('-id')
        total_records = qs.count()
        qs = self.filter_queryset(self.queryset)
        filterobject = qs.count()
        data = [self.prepare_results(car) for car in qs]
        dict = {'data': data, 'recordsFiltered':total_records}

        return JsonResponse(dict)
    

class CarHoldTimeUpdateView(HoldOwnerRequiredMixin, UpdateView):
    '''update view for car holdtime from owner'''
    model = CarHoldTime
    template_name = 'hostuser/car_hold_updateform.html'
    form_class = CarHoldTimeForm
    context_object_name = 'car'
    success_url = reverse_lazy('hostuser:holdcarlist')
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:holdcarlist')

    def form_valid(self, form):
        carhold = form.save(commit=False)
        car = form.cleaned_data['car']
        
        car = Car.objects.get(pk=car.id)
        car.is_active = False
        car.save()
        carhold.save()
        messages.success(self.request, "Car Hold Time Updated successfully!")
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
class CarHoldTimeDeleteView(HoldOwnerRequiredMixin, DeleteView):
    '''delete view for car holdtime from owner'''
    model = CarHoldTime
    template_name = 'hostuser/hold_car_list.html'
    success_url = reverse_lazy("hostuser:holdcarlist")
    login_url = '/account/login'
    redirect_field_name = reverse_lazy("hostuser:holdcarlist")
    

# End of Car HoldTime Views for CRUD


# Start of Customers List

class CustomersListView(OwnerLoginRequiredMixin, ListView):
    '''List view for display customer list of perticular owner'''
    model = Car
    context_object_name = 'customerlist'
    template_name = 'hostuser/customer_list.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:dashboard')

    def get_queryset(self):
        return Rent.objects.filter(car__owner__id=self.request.user.id).values('user__first_name', 'user__last_name', 'user__email', 'user__contact').distinct()
    
class CustomersListDataTablesAjaxPagination(OwnerLoginRequiredMixin, DataTableMixin, View):
    model = Rent
    queryset = Rent.objects.all().order_by('-id')

    def filter_queryset(self, qs):
        """Return the list of items for this view."""
        # If a search term, filter the query
        qs = Rent.objects.filter(car__owner__id=self.request.user.id).values_list('user__id', 'user__first_name', 'user__last_name', 'user__email', 'user__contact').distinct()
        start = int(self.request.GET.get("start"))
        length = int(self.request.GET.get("length"))

        if self.search:
            qs =  qs.filter(
                Q(id__icontains=self.search) |
                Q(user__first_name__icontains=self.search) |
                Q(user__last_name__icontains=self.search) |
                Q(user__email__icontains=self.search) |
                Q(user__contact__icontains=self.search) 
            )
            try:
                qs = qs[int(start):int(start)+int(length)]
            except:
                pass
    
            return qs
        
        try:
            qs = qs[int(start):int(start)+int(length)]
        except:
            pass

        return qs

    def prepare_results(self, customer):
        # Create row data for datatables
        return {
            'id': customer[0],
            'name': customer[1] + ' ' + customer[2],
            'email': customer[3],
            'contact': customer[4],
        }

    def get(self, request, *args, **kwargs):
        qs = Rent.objects.filter(car__owner__id=self.request.user.id).values_list('user__id', 'user__first_name', 'user__last_name', 'user__email', 'user__contact').distinct()
        total_records = qs.count()
        qs = self.filter_queryset(self.queryset)
        filterobject = qs.count()
        data = [self.prepare_results(customer) for customer in qs]
        dict = {'data': data, 'recordsFiltered':total_records}

        return JsonResponse(dict)
    

# End of Customers List


# Start of Profile Edit View

class HostUserProfileUpdateView(ProfileOwnerRequiredMixin, UpdateView):
    '''for hostuser update profile'''
    model = User
    context_object_name = 'user'
    form_class = UserProfileUpdateForm
    template_name = 'hostuser/hostuser_profile.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super(HostUserProfileUpdateView, self).get_context_data(**kwargs)
        context['imageform'] = UserProfileImageUpdateForm()
        context['passform'] = PasswordChangingForm(self.request.user)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy("hostuser:hostprofile", kwargs={'pk': self.kwargs['pk']})
    
# End of Profile Edit View

class HostProfileImageUpdateView(ProfileOwnerRequiredMixin, UpdateView):
    '''for update image of user profile'''
    model = User
    context_object_name = 'user'
    form_class = UserProfileImageUpdateForm
    template_name = 'hostuser/hostuser_profile.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('hostuser:dashboard')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy("hostuser:hostprofile", kwargs={'pk': self.kwargs['pk']})
    

class RevenueCompareView(OwnerLoginRequiredMixin, TemplateView):
    '''for compare top three cars by default and give custom search function and on search show result using ajax'''
    model = Rent
    context_object_name = "car"
    template_name = "hostuser/revenue_compare.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        usercars = Car.objects.filter(owner_id = self.request.user.id)

        top_cars_list = Car.objects.filter(owner_id = self.request.user.id).annotate(rent_count=Count('car_rent__car')).order_by('-rent_count')[:3]

        revenue = []
        for car in top_cars_list:
            booking = Rent.objects.filter(car__id=car.id)
            earningsum = booking.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
            earning = earningsum['total_fare__sum']
            commision_percent = 20
            commision = (earning * commision_percent) / 100
            total_net_earning = earning - commision

            earning_dict = {'car':car.id, 'totalearning':earning, 'net_commision':commision, 'net_earning':total_net_earning, 'booking':booking.count()}
            revenue.append(earning_dict)


        context["top_cars_list"] = top_cars_list
        context["revenue"] = revenue
        context["usercars"] = usercars
        return context
    

class RevenueCompareAjax(OwnerLoginRequiredMixin, View):
    '''for search cars revenue data on submit button click using ajax'''
    template_name = "hostuser/searched_revenue_compare.html"

    def get(self, request, *args, **kwargs):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        car1 = self.request.GET.get('car1')
        car2 = self.request.GET.get('car2')
        car3 = self.request.GET.get('car3')

        cars = [car1, car2, car3]
        
        revenue = []
        for car in cars:
            booking = Rent.objects.filter(car__id=car)
            car_obj = Car.objects.get(id=car)
            if booking.count() > 0:
                if start_date == "" and end_date == "":
                    earningsum = booking.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
                    earning = earningsum['total_fare__sum'] or 0
                    commision_percent = 20
                    commision = (earning * commision_percent) / 100
                    total_net_earning = earning - commision

                    earning_dict = {'car':car_obj, 'totalearning':earning, 'net_commision':commision, 'net_earning':total_net_earning, 'booking':booking.count()}

                    revenue.append(earning_dict)
                else:
                    booking = Rent.objects.filter(car__id=car).filter(drop_datetime__date__gte=start_date, drop_datetime__date__lte=end_date)
                    earningsum = booking.values_list("total_fare", flat=True).aggregate(Sum("total_fare"))
                    earning = earningsum['total_fare__sum'] or 0
                    commision_percent = 20
                    commision = (earning * commision_percent) / 100
                    total_net_earning = earning - commision

                    earning_dict = {'car':car_obj, 'totalearning':earning, 'net_commision':commision, 'net_earning':total_net_earning, 'booking':booking.count()}

                    revenue.append(earning_dict)
            else:
                earning_dict = {'car':car_obj, 'totalearning':0, 'net_commision':0, 'net_earning':0, 'booking':booking.count()}

                revenue.append(earning_dict)
        
        ranking = [revenue[0]['net_earning'], revenue[1]['net_earning'], revenue[2]['net_earning']]
        ranking =  sorted(ranking, key = lambda x:float(-x))
        
        context={
            'object_list': revenue,
            'ranking_list': ranking
        }
        response={}
        response['object_list']=render_to_string(self.template_name,context,request=request)

        return JsonResponse(response) 
    

class PasswordsChangeView(LoginRequiredMixin, PasswordChangeView):
    model = User
    # template_name = 'user/change_password.html'
    template_name = 'hostuser/hostuser_profile.html'
    form_class = PasswordChangingForm
    # form_class = PasswordChangeForm  # Built in Form
    success_url = reverse_lazy("hostuser:password_success")
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password Changed successfully!")
        return super().form_valid(form)
    

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return self.render_to_response(self.get_context_data(passform=form, form=UserProfileUpdateForm(initial={'first_name':self.request.user.first_name, 'last_name':self.request.user.last_name, 'contact':self.request.user.contact})), status=403)
    # , form=UserProfileUpdateForm(initial={'first_name':self.request.user.first_name, 'last_name':self.request.user.last_name})
    

class PasswordsChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'hostuser/password_change_success.html'

class NotificationReadAjaxView(OwnerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notification_id = request.GET.get("message_id")
        notification = Notification.objects.filter(id=notification_id)
        notification.update(is_read=True)

        return JsonResponse({"message":"Status Updated Successfully!"})