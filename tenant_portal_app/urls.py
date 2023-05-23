from django.urls import path
from . import views
from .views import user_logout, update_maintenance_request_status

urlpatterns = [
    path('', views.home, name='home'),
    path('landlord_login/', views.landlord_login, name='landlord_login'),
    path('tenant_login/', views.tenant_login, name='tenant_login'),
    path('logout/', views.user_logout, name='logout'),
    path('landlord_dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('tenant_dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('create_tenant/', views.create_tenant, name='create_tenant'),
    path('tenant_detail/<int:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('edit_tenant/<int:tenant_id>/', views.edit_tenant, name='edit_tenant'),
    path('delete_tenant/<int:tenant_id>/', views.delete_tenant, name='delete_tenant'),
    path('change_password/', views.change_password, name='change_password'),
    path('user_logout/', user_logout, name='user_logout'),
    path('submit_rent_payment/', views.submit_rent_payment, name='submit_rent_payment'),
    path('submit_maintenance_request/', views.submit_maintenance_request, name='submit_maintenance_request'),
    path('submit_message/', views.submit_message, name='submit_message'),
    path('maintenance_request_details/<int:maintenance_request_id>/', views.maintenance_request_details, name='maintenance_request_details'),
    path('mark_maintenance_request_complete/<int:maintenance_request_id>/', views.mark_maintenance_request_complete, name='mark_maintenance_request_complete'),
    path('message_details/<int:message_id>/', views.message_details, name='message_details'),
    path('maintenance_request/<int:maintenance_request_id>/update_status', update_maintenance_request_status, name='update_maintenance_request_status'),
]
