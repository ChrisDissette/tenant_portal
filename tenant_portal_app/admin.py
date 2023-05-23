from django.contrib import admin
from .models import Landlord, Tenant, CustomUser  # Import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups', 'last_login')

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Use 'email' instead of 'username'
        (('Personal info'), {'fields': ('first_name', 'last_name')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),  # Use 'email' instead of 'username'
        }),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff')  # Use 'email' instead of 'username'
    search_fields = ('email', 'first_name', 'last_name')  # Use 'email' instead of 'username'
    ordering = ('email',)  # Use 'email' instead of 'username'

if CustomUser in admin.site._registry:  # Unregister CustomUser instead of User
    admin.site.unregister(CustomUser)
admin.site.register(CustomUser, UserAdmin)  # Register CustomUser instead of User

admin.site.register(Landlord)
admin.site.register(Tenant)
