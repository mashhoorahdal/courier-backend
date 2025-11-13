from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from courier.admin_views import (
    admin_dashboard, admin_users, admin_users_create, admin_users_edit, admin_users_delete,
    admin_delivery_boys, admin_delivery_boys_create, admin_delivery_boys_edit, admin_delivery_boys_delete,
    admin_orders, admin_deliveries, admin_assign_delivery, admin_update_delivery_status, admin_logout
)


def api_v1_root(request):
    return JsonResponse({
        "message": "Courier API v1 - Hot Reload Enabled! 🚀",
        "version": "1.0",
        "endpoints": {
            "register": "/api/v1/register/",
            "token": "/api/v1/token/",
            "token_refresh": "/api/v1/token/refresh/",
            "orders": "/api/v1/orders/",
            "order_status_update": "/api/v1/orders/<id>/status/",
            "order_payment_update": "/api/v1/orders/<id>/payment/",
            "track": "/api/v1/track/<barcode>/",
            "admin": "/admin/"
        }
    })


urlpatterns = [
    path('api/v1/', api_v1_root, name='api_v1_root'),
    path('api/v1/', include('courier.urls')),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('accounts/logout/', admin_logout, name='logout'),

    # Admin Dashboard URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/users/create/', admin_users_create, name='admin_users_create'),
    path('admin/users/<int:user_id>/edit/', admin_users_edit, name='admin_users_edit'),
    path('admin/users/<int:user_id>/delete/', admin_users_delete, name='admin_users_delete'),
    path('admin/delivery-boys/', admin_delivery_boys, name='admin_delivery_boys'),
    path('admin/delivery-boys/create/', admin_delivery_boys_create, name='admin_delivery_boys_create'),
    path('admin/delivery-boys/<int:delivery_boy_id>/edit/', admin_delivery_boys_edit, name='admin_delivery_boys_edit'),
    path('admin/delivery-boys/<int:delivery_boy_id>/delete/', admin_delivery_boys_delete, name='admin_delivery_boys_delete'),
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/assign/', admin_assign_delivery, name='admin_assign_delivery'),
    path('admin/deliveries/', admin_deliveries, name='admin_deliveries'),
    path('admin/deliveries/<int:delivery_id>/update/', admin_update_delivery_status, name='admin_update_delivery_status'),
]
