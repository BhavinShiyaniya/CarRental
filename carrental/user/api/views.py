from car.models import Car
from user.models import User
from user.api.serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from user.api.permissions import IsUser
from django.db.models import Prefetch

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsUser]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

        # only gives licence number
        # return User.objects.filter(id=self.request.user.id).prefetch_related(
        #     Prefetch(
        #         'cars', 
        #         queryset=Car.objects.filter(license__is_expire=False).only("licence__number"),
        #     )
        # )


        # gives all data without licence number
         # return User.objects.filter(id=self.request.user.id).prefetch_related(
        #     Prefetch(
        #         'cars', 
        #         queryset=Car.objects.filter(license__is_expire=False).defer("licence__number"),
        #     )
        # )