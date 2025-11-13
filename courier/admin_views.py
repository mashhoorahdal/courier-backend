from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Order, UserProfile, DeliveryBoy, Delivery
from .forms import UserProfileForm, DeliveryBoyForm, DeliveryBoyEditForm


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_admin


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    # Get statistics
    stats = {
        'total_orders': Order.objects.count(),
        'delivered_orders': Order.objects.filter(status='delivered').count(),
        'total_users': User.objects.filter(profile__role='customer').count(),
        'total_delivery_boys': DeliveryBoy.objects.count(),
    }

    # Get recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]

    context = {
        'stats': stats,
        'recent_orders': recent_orders,
    }

    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """List all users with filtering"""
    users = User.objects.select_related('profile').all()

    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(profile__role=role_filter)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'role_filter': role_filter,
        'search_query': search_query,
    }

    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users_create(request):
    """Create new user"""
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('admin_users')
    else:
        user_form = UserProfileForm()

    return render(request, 'admin/user_form.html', {
        'form': user_form,
        'title': 'Create New User'
    })


@login_required
@user_passes_test(is_admin)
def admin_users_edit(request, user_id):
    """Edit existing user"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('admin_users')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'admin/user_form.html', {
        'form': form,
        'title': f'Edit User: {user.username}',
        'user': user
    })


@login_required
@user_passes_test(is_admin)
def admin_users_delete(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting self
    if user == request.user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('admin_users')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('admin_users')

    return render(request, 'admin/user_confirm_delete.html', {
        'user': user
    })


@login_required
@user_passes_test(is_admin)
def admin_delivery_boys(request):
    """List all delivery boys"""
    delivery_boys = DeliveryBoy.objects.select_related('user').all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        delivery_boys = delivery_boys.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(vehicle_number__icontains=search_query)
        )

    # Filter by availability
    availability_filter = request.GET.get('available')
    if availability_filter:
        delivery_boys = delivery_boys.filter(is_available=availability_filter == 'true')

    # Pagination
    paginator = Paginator(delivery_boys, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'availability_filter': availability_filter,
    }

    return render(request, 'admin/delivery_boys.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delivery_boys_create(request):
    """Create new delivery boy"""
    if request.method == 'POST':
        form = DeliveryBoyForm(request.POST)
        if form.is_valid():
            delivery_boy = form.save()
            messages.success(request, f'Delivery boy {delivery_boy.user.username} created successfully!')
            return redirect('admin_delivery_boys')
    else:
        form = DeliveryBoyForm()

    return render(request, 'admin/delivery_boy_form.html', {
        'form': form,
        'title': 'Create New Delivery Boy'
    })


@login_required
@user_passes_test(is_admin)
def admin_delivery_boys_edit(request, delivery_boy_id):
    """Edit existing delivery boy"""
    delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)

    if request.method == 'POST':
        form = DeliveryBoyEditForm(request.POST, instance=delivery_boy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Delivery boy {delivery_boy.user.username} updated successfully!')
            return redirect('admin_delivery_boys')
    else:
        form = DeliveryBoyEditForm(instance=delivery_boy)

    # Get completed deliveries count
    completed_deliveries = delivery_boy.deliveries.filter(status='delivered').count()

    return render(request, 'admin/delivery_boy_form.html', {
        'form': form,
        'title': f'Edit Delivery Boy: {delivery_boy.user.username}',
        'delivery_boy': delivery_boy,
        'completed_deliveries': completed_deliveries
    })


@login_required
@user_passes_test(is_admin)
def admin_delivery_boys_delete(request, delivery_boy_id):
    """Delete delivery boy"""
    delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)

    if request.method == 'POST':
        username = delivery_boy.user.username
        delivery_boy.user.delete()  # This will cascade delete the delivery boy profile
        messages.success(request, f'Delivery boy {username} deleted successfully!')
        return redirect('admin_delivery_boys')

    return render(request, 'admin/delivery_boy_confirm_delete.html', {
        'delivery_boy': delivery_boy
    })


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """List all orders"""
    orders = Order.objects.select_related('customer').all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Search by barcode or customer
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(barcode__icontains=search_query) |
            Q(customer__username__icontains=search_query) |
            Q(receiver_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(orders.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }

    return render(request, 'admin/orders.html', context)


@login_required
@user_passes_test(is_admin)
def admin_deliveries(request):
    """List all deliveries"""
    deliveries = Delivery.objects.select_related(
        'order__customer', 'delivery_boy__user'
    ).all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        deliveries = deliveries.filter(
            Q(order__barcode__icontains=search_query) |
            Q(delivery_boy__user__username__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(deliveries.order_by('-assigned_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }

    return render(request, 'admin/deliveries.html', context)


@login_required
@user_passes_test(is_admin)
def admin_assign_delivery(request, order_id):
    """Assign a delivery to a delivery boy"""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        delivery_boy_id = request.POST.get('delivery_boy')
        delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)

        # Check if delivery already exists
        if hasattr(order, 'delivery'):
            messages.error(request, 'This order already has a delivery assigned.')
            return redirect('admin_orders')

        # Create delivery assignment
        Delivery.objects.create(
            order=order,
            delivery_boy=delivery_boy,
            status='assigned'
        )

        # Update order status
        order.status = 'in_transit'
        order.save()

        messages.success(request, f'Order {order.barcode} assigned to {delivery_boy.user.get_full_name() or delivery_boy.user.username}.')
        return redirect('admin_deliveries')

    # Get available delivery boys
    available_delivery_boys = DeliveryBoy.objects.filter(is_available=True)

    context = {
        'order': order,
        'available_delivery_boys': available_delivery_boys,
    }

    return render(request, 'admin/assign_delivery.html', context)


@login_required
@user_passes_test(is_admin)
def admin_update_delivery_status(request, delivery_id):
    """Update delivery status"""
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        # Update delivery status
        if new_status == 'picked_up' and delivery.status == 'assigned':
            delivery.mark_picked_up()
            delivery.notes = notes
            delivery.save()
            messages.success(request, f'Delivery {delivery.order.barcode} marked as picked up.')

        elif new_status == 'delivered' and delivery.status in ['picked_up', 'in_transit']:
            rating = request.POST.get('rating')
            feedback = request.POST.get('feedback', '')
            delivery.mark_delivered(rating=rating, feedback=feedback)
            messages.success(request, f'Delivery {delivery.order.barcode} marked as delivered.')

        elif new_status == 'failed':
            delivery.status = 'failed'
            delivery.notes = notes
            delivery.save()
            messages.warning(request, f'Delivery {delivery.order.barcode} marked as failed.')

        return redirect('admin_deliveries')

    context = {
        'delivery': delivery,
    }

    return render(request, 'admin/update_delivery_status.html', context)


def admin_logout(request):
    """Custom logout view for admin"""
    auth.logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')
