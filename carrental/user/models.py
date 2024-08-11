from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import AbstractUser

class User(BaseModel, AbstractUser):
    '''User model for register new user'''
    contact = models.CharField(max_length=10)
    is_hostuser = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to="images/user_images", null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name