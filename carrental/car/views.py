from datetime import datetime, timezone
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from user.models import User
from car.models import Car, CarImage, Rent
from django.views.generic import DetailView, ListView, View, TemplateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from car.forms import RentForm, CarSearchForm
from django.views.generic.edit import FormMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.db.models import Q
from car.tasks import test_func, send_mail_func, send_otp
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from car.utils import schedule_send_otp
from base.permissions import UserBookingOwnerRequiredMixin
from django.contrib import messages

# Create your views here.

def home(request):
    '''for index page template testing'''
    return render(request, 'car/index.html')

def listing(request):
    '''listing page for template testing'''
    return render(request, 'car/listing.html')

def testimonials(request):
    '''listing page for template testing'''
    return render(request, 'car/testimonials.html')

def blog(request):
    '''blog page for template blog'''
    return render(request, 'car/blog.html')

def singleBlog(request):
    '''singleBlog page for template singleBlog'''
    return render(request, 'car/single.html')

def about(request):
    '''about page for template about'''
    return render(request, 'car/about.html')

def contact(request):
    '''contact page for template contact'''
    return render(request, 'car/contact.html')

def order(request):
    '''order page for template order'''
    return render(request, 'car/booking_detail.html')


class IndexView(ListView):
    '''Index page list cars'''
    model = Car
    template_name = 'car/index.html'
    context_object_name = 'carlist'

    def get_queryset(self):
        return Car.objects.exclude(owner=self.request.user.id)


class ListingView(ListView):
    '''Listing view for list all cars'''
    model = Car
    template_name = 'car/listing.html'
    context_object_name = 'carlist'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:listing')

    def get_queryset(self):
        return Car.objects.exclude(owner=self.request.user.id)


class SearchViewAjax(View):
    '''for search cars on submit button click using ajax'''
    template_name = "car/searched_car.html"

    def get(self, request, *args, **kwargs):
        pickup_datetime = self.request.GET.get("pickupdatetime")
        drop_datetime = self.request.GET.get("dropdatetime")
        car_type = self.request.GET.get('cartype')


        context={
            'object_list': Car.objects.exclude(owner=self.request.user.id).exclude(car_rent__pickup_datetime__lte=drop_datetime,car_rent__drop_datetime__gte=pickup_datetime).exclude(car_carholdtime__start_datetime__lte=drop_datetime,car_carholdtime__end_datetime__gte=pickup_datetime).filter(car_type=car_type)
        }
        response={}
        response['object_list']=render_to_string(self.template_name,context,request=request)

        return JsonResponse(response) 


class CarDetailView(DetailView):
    '''for show perticular car's detail on cardetail page'''
    model=Car
    context_object_name = 'car'
    template_name = 'car/car_detail.html'
        
    def get_context_data(self, **kwargs):
        context = super(CarDetailView, self).get_context_data(**kwargs)
        context['bookingform'] = RentForm()
        return context

    
class RentFormView(LoginRequiredMixin, CreateView):
    '''booking create form inside car detail page'''
    model = Rent
    form_class = RentForm
    context_object_name = 'rent'
    success_url = reverse_lazy('car:bookings')
    template_name = 'car/car_detail.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:listing')

    def form_valid(self, form):
        rent = form.save(commit=False)
        rent.user = self.request.user
        car = form.cleaned_data['car']
        pickup_time = form.cleaned_data["pickup_datetime"]
        drop_time = form.cleaned_data["drop_datetime"]
        
        rent.save()

        # for celery send otp mail

        task_name = str(rent.id)
        carowneremail = list(Car.objects.filter(id=car.id).values_list('owner__email', flat=True))[0]
        user_email = self.request.user.email
        to_email = [user_email, carowneremail]

        schedule_send_otp(pickup_time, to_email, task_name)

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from car.models import NotificationGroup, Notification

        channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     'indian',
        #     {
        #         'type':'chat.message',
        #         'message': 'Message from outside consumer'
        #     }
        # )

        carownername = list(Car.objects.filter(id=car.id).values_list('owner__username', flat=True))[0]
        group_name = carownername
        print("➡ group_name :", group_name)
        message = f'{self.request.user} has booked {car.brand} {car.name} - {car.registration_no}.'
        print("➡ message :", message)
       
        group = NotificationGroup.objects.get(name = group_name)
        notification = Notification(
            user = self.request.user,
            owner = car.owner,
            group = group,
            message = message,
            is_read = False
        )
        notification.save()

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send.message',
                'message': message
            }
        )

        messages.success(self.request, "Car Booked successfully!")
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    

# class HostCarDeleteView(DeleteView):
#     model = Car
#     template_name = 'hostuser/host_car_detail.html'
#     success_url = reverse_lazy("hostuser:dashboard")
#     context_object_name = 'cardelete'


class BookingListView(LoginRequiredMixin, ListView):
    '''for show list of bookings done by user'''
    model = Rent
    template_name = 'car/booking_list.html'
    context_object_name = 'bookinglist'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:bookings')

    def get_queryset(self):
        return Rent.objects.filter(user = self.request.user).order_by('-id')
    

class BookingDetailView(UserBookingOwnerRequiredMixin, DetailView):
    '''for showing detail of perticular booking'''
    model = Rent
    template_name = 'car/booking_detail.html'
    context_object_name = 'booking'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:bookings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.object
        current_datetime = datetime.now(timezone.utc)
        booking_create_time = booking.created_at

        dt_difference = current_datetime - booking_create_time
        days, seconds = dt_difference.days, dt_difference.seconds
        hours = days*24 + seconds // 3600

        if hours > 48 or booking.booking_status == "CANCELLED":
            eligible = False
        else:
            eligible = True
        context["eligible"] = eligible
        return context
    

class BookingCancelView(UserBookingOwnerRequiredMixin, View):
    '''delete view for car holdtime from owner'''
    model = Rent

    def post(self, *args, **kwargs):
        id = self.request.POST.get("id")
        booking = Rent.objects.get(pk=id)
        booking.booking_status = "CANCELLED"
        booking.save()
        messages.success(self.request, "Booking Cancelled successfully!")
        return HttpResponseRedirect(reverse_lazy('car:bookings')) 
    


    
# =========================================================================================================
# celery learning
def test(request):
    test_func.delay()
    return HttpResponse("Done")

def send_mail_to_all(request):
    send_mail_func.delay()
    return HttpResponse("Sent")

def schedule_mail(request):
    print("smsmsmsmmsmsm")
    schedule, created = CrontabSchedule.objects.get_or_create(hour = 17, minute = 16)
    task = PeriodicTask.objects.create(crontab=schedule, name="schedule_mail_task_"+"13", task="car.tasks.send_mail_func") #, args = json.dumps(([2,3])))
    print("task:::", task)
    return HttpResponse("Done")
