from django.urls import path, include
from rest_framework.routers import DefaultRouter
from car.api.views import (
                            CarViewSet,
                            CarImageViewSet,
                            CarHoldTimeViewSet,
                            RentViewSet,
                            DashboardAPI,
                            RevenueApi,
                            )

router = DefaultRouter()
router.register('car', CarViewSet, basename='car')
router.register('carimage', CarImageViewSet, basename='carimage')
router.register('carholdtime', CarHoldTimeViewSet, basename='carholdtime')
router.register('rent', RentViewSet, basename='rent')
router.register('revenue', RevenueApi, basename='revenue')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboardapi/', DashboardAPI.as_view(), name='dashboardapi'),
    path('dashboardapi/<int:pk>', DashboardAPI.as_view(), name='dashboardapi'),
    # path('revenue/', RevenueApi.as_view(), name='revenue'),
]

