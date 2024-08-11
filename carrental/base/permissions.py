from django.contrib.auth.mixins import LoginRequiredMixin
from user.models import User
from car.models import Car, Rent, CarImage, CarHoldTime

class OwnerLoginRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        
        return self.request.user.is_hostuser
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    

class OwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        car = Car.objects.filter(id=self.kwargs['pk']).filter(owner=self.request.user)
        
        return self.request.user.is_hostuser and car
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
class BookingOwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        car = Rent.objects.filter(id=self.kwargs['pk']).filter(car__owner__id=self.request.user.id)
        
        return self.request.user.is_hostuser and car
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
class ImageOwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        car = CarImage.objects.filter(id=self.kwargs['pk']).filter(car__owner__id=self.request.user.id)

        
        return self.request.user.is_hostuser and car
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
class HoldOwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        car = CarHoldTime.objects.filter(id=self.kwargs['pk']).filter(car__owner__id=self.request.user.id)

        
        return self.request.user.is_hostuser and car
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
class ProfileOwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        # car = User.objects.filter(id=self.kwargs['pk']).filter(car__owner__id=self.request.user.id)

        return self.request.user and self.kwargs['pk'] == self.request.user.id
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
class UserBookingOwnerRequiredMixin(LoginRequiredMixin):
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        car = Rent.objects.filter(id=self.kwargs['pk']).filter(user__id=self.request.user.id)
        
        return self.request.user and car
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
