from django.urls import path
from car.views import (
                    home, 
                    listing, 
                    testimonials, 
                    about, 
                    contact, 
                    blog, 
                    singleBlog, 
                    ListingView, 
                    CarDetailView, 
                    order, 
                    RentFormView, 
                    IndexView, 
                    BookingListView, 
                    BookingDetailView, 
                    BookingCancelView,
                    SearchViewAjax, 
                    test, 
                    send_mail_to_all, 
                    schedule_mail)
from car.utils import msgfromoutside
app_name = 'car'

urlpatterns = [
    # for index
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name='index'),

    # for search and list operations
    path('listing/', ListingView.as_view(), name='listing'),
    path('searchview/',SearchViewAjax.as_view(),name='searchviewajax'),

    # for rent operations
    path('cardetail/<int:pk>', CarDetailView.as_view(), name='cardetail'),
    path('rent/', RentFormView.as_view(), name='rent'),

    # for bookings operations
    path('bookings/', BookingListView.as_view(), name='bookings'),
    path('bookingdetail/<int:pk>', BookingDetailView.as_view(), name='bookingdetail'),
    path('bookingcancel/<int:pk>', BookingCancelView.as_view(), name='bookingcancel'),

    # for celery learning
    path('test/', test, name='test'),
    path('sendmail/', send_mail_to_all, name='sendmail'),
    path('schedulemail/', schedule_mail, name='schedulemail'),


    # for template testing only
    path('home/', home, name='home'),
    path('alllisting/', listing, name='alllisting'),
    path('testimonials/', testimonials, name='testimonials'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('blog/', blog, name='blog'),
    path('single/', singleBlog, name='single'),


    path('msg/', msgfromoutside, name='msg')
]
