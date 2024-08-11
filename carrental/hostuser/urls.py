from django.urls import path
from hostuser.views import (
                            DashboardView, 
                            AjaxRevenueChartDataView,
                            HostCarDetailView, 
                            HostUserProfileUpdateView,
                            HostProfileImageUpdateView, 
                            CarListView, 
                            CarListDataTablesAjaxPagination,
                            CarUpdateView, 
                            CarDeleteView, 
                            HostBookingListView, 
                            HostBookingListDataTablesAjaxPagination,
                            HostBookingDetailView, 
                            HostBookingUpdateView, 
                            CarHoldTimeCreateView, 
                            HoldCarListView, 
                            HoldCarListDataTablesAjaxPagination,
                            CarHoldTimeUpdateView, 
                            CarHoldTimeDeleteView,
                            AjaxCarAvailabilityCheckView,
                            CustomersListView,
                            CustomersListDataTablesAjaxPagination,
                            SingleCarImageDeleteView,
                            RevenueCompareView,
                            RevenueCompareAjax,
                            PasswordsChangeView,
                            PasswordsChangeDoneView,
                            NotificationReadAjaxView,
                        )
# from car.views import HostCarDeleteView

app_name = 'hostuser'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('revenue-chart-ajax/', AjaxRevenueChartDataView.as_view(), name='revenue-chart-ajax'),

    # car CRUD (Car create view is inside user app)
    path('carlist/', CarListView.as_view(), name='carlist'),
    path('car-list-ajax/',CarListDataTablesAjaxPagination.as_view(), name='car-list-ajax'),
    path('carupdate/<int:pk>', CarUpdateView.as_view(), name='carupdate'),
    path('hostcardetail/<int:pk>', HostCarDetailView.as_view(), name='hostcardetail'),
    path('cardelete/<int:pk>', CarDeleteView.as_view(), name='cardelete'),
    path('singlecarimagedelete/<int:pk>', SingleCarImageDeleteView.as_view(), name='singlecarimagedelete'),

    # update profile
    path('hostprofile/<int:pk>', HostUserProfileUpdateView.as_view(), name='hostprofile'),
    path('hostprofileimageupdate/<int:pk>', HostProfileImageUpdateView.as_view(), name='hostprofileimageupdate'),

    # booking CRUD
    path('hostbookinglist/', HostBookingListView.as_view(), name='hostbookinglist'),
    path('booking-list-ajax/',HostBookingListDataTablesAjaxPagination.as_view(), name='booking-list-ajax'),
    path('hostbookingdetail/<int:pk>', HostBookingDetailView.as_view(), name='hostbookingdetail'),
    path('hostbookingupdate/<int:pk>', HostBookingUpdateView.as_view(), name='hostbookingupdate'),

    # car hold CRUD
    path('carhold/', CarHoldTimeCreateView.as_view(), name='carhold'),
    path('holdcarlist/', HoldCarListView.as_view(), name='holdcarlist'),
    path('hold-car-list-ajax/',HoldCarListDataTablesAjaxPagination.as_view(), name='hold-car-list-ajax'),
    path('carholdupdate/<int:pk>', CarHoldTimeUpdateView.as_view(), name='carholdupdate'),
    path('carholddelete/<int:pk>', CarHoldTimeDeleteView.as_view(), name='carholddelete'),

    # check car availability using ajax
    path("ajax-car-availability/", AjaxCarAvailabilityCheckView.as_view(),  name="ajax_car_availability_check"),

    # customers list
    path('customerslist/', CustomersListView.as_view(), name='customerslist'),
    path('customers-list-ajax/',CustomersListDataTablesAjaxPagination.as_view(), name='customers-list-ajax'),

    # revenue compare
    path('revenue-compare/', RevenueCompareView.as_view(), name="revenue-compare"),
    path('revenue-compare-ajax/', RevenueCompareAjax.as_view(), name="revenue-compare-ajax"),


    # password change
    path('password_change/', PasswordsChangeView.as_view(), name='password_change'),
    path('password_success/', PasswordsChangeDoneView.as_view(), name='password_success'),

    # notification
    path('notification_read_status/', NotificationReadAjaxView.as_view(), name='notification_read_status'),
]