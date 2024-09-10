from django.contrib.auth.base_user import BaseUserManager
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


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)

        # Добавляем дополнительные поля в user
        first_name = extra_fields.pop('first_name', '')
        last_name = extra_fields.pop('last_name', '')
        phone = extra_fields.pop('phone', '')
        role = extra_fields.pop('role', '')
        sub_role = extra_fields.pop('sub_role', None)
        gender = extra_fields.pop('gender', '')
        date_birth = extra_fields.pop('date_birth', None)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            sub_role=sub_role,
            gender=gender,
            date_birth=date_birth,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    avatar = models.ImageField(upload_to='users_avatars', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    sub_role = models.ForeignKey(SubRole, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



