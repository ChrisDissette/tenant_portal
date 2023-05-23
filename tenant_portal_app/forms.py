from django import forms
from django.forms import DateInput
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Tenant, MaintenanceRequest, Message, RentPayment, CustomUser

class TenantForm(forms.ModelForm):
    lease_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    lease_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Tenant
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'apartment_number',
            'lease_pdf', 'lease_start', 'lease_end', 'monthly_rent'
        ]

    def __init__(self, *args, **kwargs):
        super(TenantForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'Phone Number', 'class': 'form-control'})
        self.fields['apartment_number'].widget.attrs.update({'placeholder': 'Apartment Number', 'class': 'form-control'})
        self.fields['monthly_rent'].widget.attrs.update({'placeholder': 'Monthly Rent', 'class': 'form-control'})

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'tenant-form-input'})


    def clean_email(self):
        email = self.cleaned_data['email']
        current_tenant_id = self.instance.id  # Get the current tenant id, if any

        # Check if the email is associated with another tenant
        other_tenants = Tenant.objects.filter(email=email).exclude(id=current_tenant_id)

        if other_tenants.exists():
            raise ValidationError("A tenant with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data



class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'content']

class RentPaymentForm(forms.ModelForm):
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Payment Date'
    )

    class Meta:
        model = RentPayment
        fields = ['amount', 'payment_date']

