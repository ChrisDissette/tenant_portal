from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Landlord(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Updated
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email

class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Updated
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10)
    lease_pdf = models.FileField(upload_to='leases/')
    lease_start = models.DateField()
    lease_end = models.DateField()
    monthly_rent = models.DecimalField(max_digits=7, decimal_places=2)
    roommate = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class RentPayment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    payment_date = models.DateField()

class MaintenanceRequest(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=100)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    description = models.TextField()
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

class Message(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=100)
    content = models.TextField()
    submitted_date = models.DateTimeField(auto_now_add=True)
