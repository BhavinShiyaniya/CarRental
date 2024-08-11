from django.urls import path
from user.views import (
                        UserRegisterView, 
                        registerOptionView, 
                        RegisterOptionView,
                        LoginView, 
                        CarRegisterView,
                        UserProfileUpdateView,
                        ProfileImageUpdateView,
                        PasswordsChangeView,
                        PasswordsChangeDoneView,
                        )

app_name = 'user'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    # path('account/login/', LoginView.as_view(), name='login'),

    # path('registeroption/', registerOptionView, name='registeroption'),
    path('registeroption/', RegisterOptionView.as_view(), name='registeroption'),
    path('carregister/', CarRegisterView.as_view(), name='carregister'),

    # update profile
    path('profile/<int:pk>', UserProfileUpdateView.as_view(), name='profile'),
    path('profileimageupdate/<int:pk>', ProfileImageUpdateView.as_view(), name='profileimageupdate'),

    # password change
    path('password_change/', PasswordsChangeView.as_view(), name='password_change'),
    path('password_success/', PasswordsChangeDoneView.as_view(), name='password_success'),
]
