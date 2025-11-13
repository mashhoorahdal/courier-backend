from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_v1_root(request):
    return JsonResponse({
        "message": "Courier API v1",
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
    path('admin/', admin.site.urls),
    path('api/v1/', api_v1_root, name='api_v1_root'),
    path('api/v1/', include('courier.urls')),
]
