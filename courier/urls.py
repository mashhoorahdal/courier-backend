from django.urls import path
from .views import (
    RegisterView,
    OrderListCreateView,
    TrackOrderView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    OrderStatusUpdateView,
    OrderPaymentUpdateView
)

app_name = 'courier'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('orders/<int:pk>/payment/', OrderPaymentUpdateView.as_view(), name='order_payment_update'),
    path('track/<str:barcode>/', TrackOrderView.as_view(), name='track_order'),
]
