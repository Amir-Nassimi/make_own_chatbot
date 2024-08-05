from uuid import uuid4 as UUID

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from Auth.models import CustomUserManager



class Users(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=UUID, primary_key=True, unique=True, editable=False)

    last_name = models.TextField()
    first_name = models.TextField()
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'

    @property
    def Joined(self):
        return self.date_joined.strftime("%Y/%m/%d %H:%M:%S")
