from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserRole, UserPermission, AdminUser, ActivityLog, UserProfile, UserActivity
from .forms import UserRoleForm, UserPermissionForm, AdminUserForm, AddProductForm, UserProfileForm
from django.utils import timezone
from core.models import CartOrder, Product, Category, ProductReview
from django.db.models import Sum, Count
from userauths.models import User
import datetime

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or AdminUser.objects.filter(user=user, is_active=True).exists())

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics for the dashboard
    total_revenue = CartOrder.objects.filter(paid_status='paid').aggregate(Sum('price'))
    total_orders = CartOrder.objects.count()
    total_products = Product.objects.count()
    monthly_revenue = CartOrder.objects.filter(
        paid_status='paid',
        order_date__month=timezone.now().month
    ).aggregate(Sum('price'))

    # Get recent orders
    latest_orders = CartOrder.objects.all().order_by('-order_date')[:10]

    context = {
        'revenue': total_revenue,
        'total_orders_count': {'count': total_orders},
        'all_products': {'count': total_products},
        'monthly_revenue': monthly_revenue,
        'latest_orders': latest_orders,
    }
    return render(request, 'useradmin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'useradmin/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def role_list(request):
    roles = UserRole.objects.all()
    context = {
        'roles': roles
    }
    return render(request, 'useradmin/role_list.html', context)

@login_required
@user_passes_test(is_admin)
def activity_logs(request):
    logs = ActivityLog.objects.all()
    context = {
        'logs': logs
    }
    return render(request, 'useradmin/activity_logs.html', context)

@login_required
@user_passes_test(is_admin)
def manage_permissions(request):
    permissions = UserPermission.objects.all()
    context = {
        'permissions': permissions
    }
    return render(request, 'useradmin/manage_permissions.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    try:
        role = user.userrole
    except UserRole.DoesNotExist:
        role = UserRole.objects.create(user=user)
    
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'user': user,
        'profile': profile,
        'role': role,
        'activities': activities,
    }
    return render(request, 'useradmin/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def edit_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User profile updated successfully.')
            return redirect('useradmin:user_detail', user_id=user.id)
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'useradmin/edit_user_profile.html', context)

@login_required
@user_passes_test(is_admin)
def edit_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        role = user.userrole
    except UserRole.DoesNotExist:
        role = UserRole.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.assigned_by = request.user
            role.save()
            messages.success(request, 'User role updated successfully.')
            return redirect('useradmin:user_detail', user_id=user.id)
    else:
        form = UserRoleForm(instance=role)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'useradmin/edit_user_role.html', context)

@login_required
@user_passes_test(is_admin)
def user_activity_log(request, user_id):
    user = get_object_or_404(User, id=user_id)
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')
    
    context = {
        'user': user,
        'activities': activities,
    }
    return render(request, 'useradmin/user_activity_log.html', context)

@login_required
@user_passes_test(is_admin)
def product_list(request):
    all_products = Product.objects.all().order_by('-id')
    all_categories = Category.objects.all()
    
    context = {
        'all_products': all_products,
        'all_categories': all_categories,
    }
    return render(request, 'useradmin/products.html', context)

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_form = form.save(commit=False)
                new_form.user = request.user
                new_form.save()
                
                # Handle tags
                if form.cleaned_data.get('tags'):
                    tag_list = [tag.strip() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]
                    new_form.tags.add(*tag_list)
                
                form.save_m2m()
                messages.success(request, 'Product added successfully!')
                return redirect('useradmin:product-list')
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
    else:
        form = AddProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product',
    }
    return render(request, 'useradmin/add-product.html', context)

@login_required
@user_passes_test(is_admin)
def order_list(request):
    orders = CartOrder.objects.all().order_by('-date')
    context = {
        'orders': orders
    }
    return render(request, 'useradmin/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def review_list(request):
    reviews = ProductReview.objects.all().order_by('-date')
    context = {
        'reviews': reviews
    }
    return render(request, 'useradmin/review_list.html', context)

@login_required
@user_passes_test(is_admin)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('useradmin:dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form
    }
    return render(request, 'useradmin/change_password.html', context)

@login_required
@user_passes_test(is_admin)
def product(request):
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    
    context = {
        "all_products": all_products,
        "all_categories": all_categories,
    }
    
    return render(request, "useradmin/products.html", context)

@login_required
@user_passes_test(is_admin)
def edit_product(request, pid):
    product = get_object_or_404(Product, pid=pid)
    
    # Convert tags to comma-separated string for initial form data
    initial_data = None
    if product.tags.exists():
        initial_data = {'tags': ', '.join([tag.name for tag in product.tags.all()])}
    
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                new_form = form.save(commit=False)
                new_form.user = request.user
                new_form.save()
                
                # Handle tags
                if form.cleaned_data.get('tags'):
                    # Clear existing tags and add new ones
                    product.tags.clear()
                    tag_list = [tag.strip() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]
                    product.tags.add(*tag_list)
                
                form.save_m2m()
                messages.success(request, 'Product updated successfully!')
                return redirect('useradmin:product-list')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
    else:
        form = AddProductForm(instance=product, initial=initial_data)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Edit Product',
    }
    return render(request, 'useradmin/edit-product.html', context)

@login_required
@user_passes_test(is_admin)
def delete_product(request, pid):
    if request.method == 'POST':
        product = get_object_or_404(Product, pid=pid)
        product_title = product.title
        product.delete()
        messages.success(request, f'Product "{product_title}" has been deleted successfully.')
        return redirect('useradmin:product-list')
    return redirect('useradmin:product-list')
