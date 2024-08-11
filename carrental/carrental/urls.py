"""
URL configuration for carrental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user.views import LoginView, LogoutView

from django.conf.urls import handler400, handler403, handler404, handler500
from base.views import handler403 as customhandler403
from base.views import handler404 as customhandler404

# JWT Auth imports
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('user/', include('user.urls')),
    path('', include('car.urls')),
    path('hostuser/', include('hostuser.urls')),

    path('account/login/', LoginView.as_view(), name='account_login'),
    path('account/logout/', LogoutView.as_view(), name='account_logout'),
    
    # for giving login option in api page
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),

    # ===============================
    # JWT AUTHENTICATION VIEWS URLS #
    # ===============================
    path('gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # For generate token JWT = http POST http://127.0.0.1:8000/gettoken/ username="<username>" password="<password>"
    
    path('refreshtoken/', TokenRefreshView.as_view(), name='token_refresh'),
    # For refresh token JWT = http POST http://127.0.0.1:8000/refreshtoken/ refresh="<refresh token>"


    path('verifytoken/', TokenVerifyView.as_view(), name='token_verify'),
    # For verify token JWT = http POST http://127.0.0.1:8000/verifytoken/ token="<access token>"

    path('api/user/', include('user.api.urls')),
    path('api/car/', include('car.api.urls')),
]

handler404 = handler400 = handler500 = customhandler404            
handler403 = customhandler403


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
