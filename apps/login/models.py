from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, **extra_fields):  # Set email as an optional parameter
        if not username:
            raise ValueError('The username field must be set')
        if email:  # Normalize email only if it's provided
            email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, **extra_fields):  # Set email as an optional parameter
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, email, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)  # Email is optional
    note_password = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    name_bank = models.CharField(max_length=255, blank=True, null=True)
    bank_number = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'