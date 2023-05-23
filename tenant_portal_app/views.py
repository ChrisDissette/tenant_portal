from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from .models import Landlord, Tenant, MaintenanceRequest, Message, RentPayment, CustomUser
from .forms import RentPaymentForm, TenantForm, MaintenanceRequestForm, MessageForm
from datetime import date
import uuid
from django.views.decorators.http import require_POST

def home(request):
    return render(request, 'home.html')


@login_required
def create_tenant(request):
    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new user for the tenant
            tenant_email = form.cleaned_data['email']
            tenant_username = tenant_email.split('@')[0] + "_" + str(uuid.uuid4())[:8]
            tenant_password = 'password'
            # Replace 'User' with 'CustomUser'
            tenant_user = CustomUser.objects.create_user(email=tenant_email, password=tenant_password)

            # Save the tenant with the associated user
            tenant = form.save(commit=False)
            tenant.user = tenant_user
            tenant.landlord = request.user.landlord
            tenant.save()
            return redirect('landlord_dashboard')
    else:
        form = TenantForm()
    return render(request, 'create_tenant.html', {'form': form})


def landlord_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            try:
                landlord = user.landlord
                login(request, user)
                return redirect('landlord_dashboard')
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid landlord credentials')
                print("Landlord not found")
        else:
            messages.error(request, 'Invalid login credentials')
            print("Invalid login credentials")
    return render(request, 'landlord_login.html', {})




def tenant_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)  # Use 'username' instead of 'email'
        if user is not None and hasattr(user, 'tenant'):
            login(request, user)
            if user.tenant.is_first_login:
                return redirect('change_password')  # Redirect to change password if it's the tenant's first login
            return redirect('tenant_dashboard')
        else:
            messages.error(request, 'Invalid tenant credentials')
    return render(request, 'tenant_login.html')




@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def landlord_dashboard(request):
    if request.user.is_authenticated:
        try:
            landlord = Landlord.objects.get(user=request.user)
            tenants = Tenant.objects.filter(landlord=landlord)
            messages = Message.objects.filter(tenant__in=tenants)

            # Check if show_completed in request.GET
            show_completed = 'show_completed' in request.GET

            if show_completed:
                maintenance_requests = MaintenanceRequest.objects.filter(tenant__in=tenants, status__in=['Pending', 'In Progress', 'Completed'])  # Added 'Completed'
            else:
                maintenance_requests = MaintenanceRequest.objects.filter(tenant__in=tenants, status__in=['Pending', 'In Progress'])

            tenants_31_60_days = [t for t in tenants if 31 <= (t.lease_end - date.today()).days <= 60]
            tenants_0_30_days = [t for t in tenants if 0 <= (t.lease_end - date.today()).days <= 30]

            for tenant in tenants_31_60_days + tenants_0_30_days:
                tenant.days_remaining = (tenant.lease_end - date.today()).days
                if tenant.days_remaining == 0:
                    tenant.days_remaining = "Today"

            context = {
                'tenants': tenants,
                'maintenance_requests': maintenance_requests,
                'messages': messages,
                'tenants_31_60_days': tenants_31_60_days,
                'tenants_0_30_days': tenants_0_30_days,
                'show_completed': show_completed
            }

            return render(request, 'landlord_dashboard.html', context)
        except Landlord.DoesNotExist:
            pass

    return HttpResponseRedirect(reverse('user_login'))



@require_POST
@login_required
def update_maintenance_request_status(request, maintenance_request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=maintenance_request_id)
    new_status = request.POST.get('status')
    if new_status in dict(MaintenanceRequest.STATUS_CHOICES):
        maintenance_request.status = new_status
        maintenance_request.save()
    return HttpResponseRedirect(reverse('maintenance_request_details', args=[maintenance_request.pk]))


@login_required
def tenant_dashboard(request):
    if not hasattr(request.user, 'tenant'):
        return redirect('home')
    
    tenant = request.user.tenant
    
    # Query RentPayment, MaintenanceRequest, and Message models for the current tenant
    payments = RentPayment.objects.filter(tenant=tenant)
    maintenance_requests = MaintenanceRequest.objects.filter(tenant=tenant)
    messages = Message.objects.filter(tenant=tenant)
    
    # Pass the querysets to the template context
    context = {
        'tenant': tenant,
        'payments': payments,
        'maintenance_requests': maintenance_requests,
        'messages': messages
    }
    
    return render(request, 'tenant_dashboard.html', context)

@login_required
def tenant_detail(request, tenant_id):
    try:
        tenant = Tenant.objects.get(id=tenant_id, landlord=request.user.landlord)
    except Tenant.DoesNotExist:
        return redirect('landlord_dashboard')
    return render(request, 'tenant_detail.html', {'tenant': tenant})

@login_required
def edit_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            form.save()
            return redirect('landlord_dashboard')
    else:
        form = TenantForm(instance=tenant)
    return render(request, 'edit_tenant.html', {'form': form})

@login_required
def delete_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    user = tenant.user
    if request.method == 'POST':
        tenant.delete()
        user.delete()
        return redirect('landlord_dashboard')
    return render(request, 'delete_tenant.html', {'tenant': tenant})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after the password change
            tenant = request.user.tenant
            tenant.is_first_login = False
            tenant.save()
            return redirect('tenant_dashboard')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def submit_rent_payment(request):
    if not hasattr(request.user, 'tenant'):
        return redirect('home')
    tenant = request.user.tenant
    if request.method == 'POST':
        form = RentPaymentForm(request.POST)
        if form.is_valid():
            rent_payment = form.save(commit=False)
            rent_payment.tenant = tenant
            rent_payment.save()
            return redirect('tenant_dashboard')
    else:
        form = RentPaymentForm()
    return render(request, 'submit_rent_payment.html', {'form': form})

@login_required
def submit_maintenance_request(request):
    if not hasattr(request.user, 'tenant'):
        return redirect('home')
    tenant = request.user.tenant
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.tenant = tenant
            maintenance_request.save()
            return redirect('tenant_dashboard')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'submit_maintenance_request.html', {'form': form})

@login_required
def submit_message(request):
    if not hasattr(request.user, 'tenant'):
        return redirect('home')
    tenant = request.user.tenant
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.tenant = tenant
            message.save()
            return redirect('tenant_dashboard')
    else:
        form = MessageForm()
    return render(request, 'submit_message.html', {'form': form})


def maintenance_request_details(request, maintenance_request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=maintenance_request_id)
    return render(request, 'maintenance_request_details.html', {'maintenance_request': maintenance_request})

def mark_maintenance_request_complete(request, maintenance_request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=maintenance_request_id)
    maintenance_request.status = 'Completed'
    maintenance_request.save()
    return HttpResponseRedirect(reverse('landlord_dashboard'))


def message_details(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    return render(request, 'message_details.html', {'message': message})
