from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        if email:
            email = self.normalize_email(email)
        else:
            email = None

        # Добавляем дополнительные поля в user
        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        phone = extra_fields.pop('phone', None)
        role = extra_fields.pop('role', None)
        sub_role = extra_fields.pop('sub_role', None)
        access_key = extra_fields.pop('access_key', None)
        gender = extra_fields.pop('gender', None)
        date_birth = extra_fields.pop('date_birth', None)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            sub_role=sub_role,
            gender=gender,
            access_key=access_key,
            date_birth=date_birth,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        admin = Role.objects.get(role='admin')

        # Устанавливаем значения по умолчанию для обязательных полей
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', admin)
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to='users_avatars', blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    access_key = models.CharField(max_length=20, blank=True, null=True, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    sub_role = models.ForeignKey(SubRole, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



