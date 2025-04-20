from django.urls import path
from useradmin import views

app_name = 'useradmin'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_list, name='user-list'),
    path('roles/', views.role_list, name='role-list'),
    path('activity-logs/', views.activity_logs, name='activity-logs'),
    path('permissions/', views.manage_permissions, name='manage-permissions'),
    path('products/', views.product_list, name='product-list'),
    path('products/add/', views.add_product, name='add-product'),
    path('products/edit/<str:pid>/', views.edit_product, name='edit-product'),
    path('products/delete/<str:pid>/', views.delete_product, name='delete-product'),
    path('orders/', views.order_list, name='order-list'),
    path('reviews/', views.review_list, name='review-list'),
    path('change-password/', views.change_password, name='change-password'),
] 