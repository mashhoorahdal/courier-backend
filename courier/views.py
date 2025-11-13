from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Order
from .serializers import RegisterSerializer, OrderSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated


# User Registration
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []  # Allow unauthenticated registration


# List/Create Orders
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


# Custom Token Obtain View
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Custom Token Refresh View
class CustomTokenRefreshView(TokenRefreshView):
    pass  # Uses default serializer


# Update Order Status
class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, customer=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status is required"}, status=400)

        if order.update_status(new_status):
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({"error": "Invalid status transition"}, status=400)


# Update Payment Status
class OrderPaymentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, customer=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        action = request.data.get('action')
        if action == 'pay':
            if order.mark_as_paid():
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response({"error": "Order is already paid"}, status=400)
        elif action == 'refund':
            if order.refund_payment():
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response({"error": "Order cannot be refunded"}, status=400)
        else:
            return Response({"error": "Invalid action. Use 'pay' or 'refund'"}, status=400)


# Track order by barcode (public)
class TrackOrderView(APIView):
    permission_classes = []  # Allow public access

    def get(self, request, barcode):
        try:
            order = Order.objects.get(barcode=barcode)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
