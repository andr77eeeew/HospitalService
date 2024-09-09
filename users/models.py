from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    role = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.role


class SubRole(models.Model):
    main_role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    sub_role = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.sub_role


class User(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatars', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    sub_role = models.ForeignKey(SubRole, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"