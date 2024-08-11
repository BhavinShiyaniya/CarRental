from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from user.models import User
from user.forms import UserRegisterForm, CarRegisterForm, CarImagesForm, UserProfileUpdateForm, UserProfileImageUpdateForm, PasswordChangingForm
from car.models import Car, CarImage, NotificationGroup
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from base.permissions import ProfileOwnerRequiredMixin
from django.contrib import messages

# Create your views here.


class UserRegisterView(CreateView):
    '''for register a user by create view'''
    model = User
    form_class = UserRegisterForm
    template_name = 'user/user_register.html'
    success_url = reverse_lazy('user:registeroption')
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'user'
        return super().get_context_data(**kwargs)
    
    # def form_valid(self, form):
    #     user = form.save()
    #     username = self.request.POST['username']
    #     password = self.request.POST['password1']
    #     #authenticate user then login
    #     user = authenticate(username=username, password=password)
    #     login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
    #     # login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
    #     return super().form_valid(form)
    
    def form_valid(self, form):
        view = super(UserRegisterView, self).form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]

        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, "User Registered successfully!")
        return view
        
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    
    
# def loginview(request):
#     return render(request, 'user/user_login.html')

    
class LoginView(LoginView):
    '''login view'''
    template_name = 'user/user_login.html'

    redirect_authenticated_user=True

    def get_redirect_url(self):

        if self.request.user.is_authenticated:
            if self.request.user.is_hostuser:
                return reverse_lazy("hostuser:dashboard")
            else:
                return reverse_lazy("car:index")
            

            

class LogoutView(LogoutView):
    '''logout view'''
    def get_redirect_url(self):
        return reverse_lazy("car:index")



def registerOptionView(request):
    '''gives an option to user after register for become a hostuser'''
    return render(request, 'user/register_option.html')

class RegisterOptionView(LoginRequiredMixin, TemplateView):
    template_name = 'user/register_option.html'

class CarRegisterView(LoginRequiredMixin, CreateView):
    '''register a car using create view form'''
    model = Car
    form_class = CarRegisterForm
    template_name = 'user/car_register.html'
    success_url = reverse_lazy('hostuser:carlist')
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('user:carregister')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["carimages"] = CarImagesForm
        return context
    
    def form_valid(self, form):
        car = form.save(commit=False)

        car.owner = self.request.user
        car.is_available = True

        # change user type
        user = User.objects.get(pk=self.request.user.id)
        user.is_hostuser = True
        user.save()

        car.save()
        
        car_images = self.request.FILES.getlist("car_images")
        for img in car_images:
            CarImage.objects.create(car=car, car_images=img)

        group = NotificationGroup.objects.filter(name = self.request.user.username).first()
        if not group:
            group = NotificationGroup(name = self.request.user.username)
            group.save()

        messages.success(self.request, "Car Registered successfully!")
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    
# Start of Profile Edit View

class UserProfileUpdateView(ProfileOwnerRequiredMixin, UpdateView):
    '''for hostuser update profile'''
    model = User
    context_object_name = 'user'
    form_class = UserProfileUpdateForm
    template_name = 'user/user_profile.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:index')
    
    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        context['imageform'] = UserProfileImageUpdateForm()
        context['passform'] = PasswordChangingForm(self.request.user)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy("user:profile", kwargs={'pk': self.kwargs['pk']})
    
# End of Profile Edit View

class ProfileImageUpdateView(ProfileOwnerRequiredMixin, UpdateView):
    '''for update image of user profile'''
    model = User
    context_object_name = 'user'
    form_class = UserProfileImageUpdateForm
    template_name = 'user/user_profile.html'
    login_url = '/account/login'
    redirect_field_name = reverse_lazy('car:index')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
    def get_success_url(self):
        return reverse_lazy("user:profile", kwargs={'pk': self.kwargs['pk']})


class PasswordsChangeView(LoginRequiredMixin, PasswordChangeView):
    model = User
    # template_name = 'user/change_password.html'
    template_name = 'user/user_profile.html'
    form_class = PasswordChangingForm
    # form_class = PasswordChangeForm  # Built in Form
    success_url = reverse_lazy("user:password_success")
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password Changed successfully!")
        return super().form_valid(form)
    

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return self.render_to_response(self.get_context_data(passform=form, form=UserProfileUpdateForm(initial={'first_name':self.request.user.first_name, 'last_name':self.request.user.last_name, 'contact':self.request.user.contact})), status=201)
    # , form=UserProfileUpdateForm(initial={'first_name':self.request.user.first_name, 'last_name':self.request.user.last_name})
    

# def PasswordsChangeDoneView(request):
#     return render(request, 'user/password_change_success.html', {})

class PasswordsChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'user/password_change_success.html'
