from django.contrib import admin
from core.models import Coupon, Product, Category, Vendor, CartOrder, CartOrderItem, ProductImages, ProductReview, Wishlist, Address

# تخصيص شكل لوحة التحكم
admin.site.site_header = 'E-commerce Admin'
admin.site.site_title = 'E-commerce Admin Portal'
admin.site.index_title = 'Welcome to E-commerce Admin Portal'

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ['image', 'is_feature']
    max_num = 5

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'product_image', 'price', 'category', 'vendor', 'featured', 'product_status', 'pid', 'stock_count', 'date']
    list_filter = ['product_status', 'featured', 'category', 'vendor', 'date']
    search_fields = ['title', 'description', 'pid']
    list_editable = ['featured', 'product_status', 'price', 'stock_count']
    readonly_fields = ['pid', 'date']
    date_hierarchy = 'date'
    actions = ['make_featured', 'make_unfeatured', 'mark_as_published', 'mark_as_draft']
    list_per_page = 25
    ordering = ['-date']
    
    def make_featured(self, request, queryset):
        queryset.update(featured=True)
    make_featured.short_description = "Mark selected products as featured"
    
    def make_unfeatured(self, request, queryset):
        queryset.update(featured=False)
    make_unfeatured.short_description = "Mark selected products as unfeatured"
    
    def mark_as_published(self, request, queryset):
        queryset.update(product_status='published')
    mark_as_published.short_description = "Mark selected products as published"
    
    def mark_as_draft(self, request, queryset):
        queryset.update(product_status='draft')
    mark_as_draft.short_description = "Mark selected products as draft"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'product_count']
    search_fields = ['title']
    readonly_fields = ['cid']
    list_per_page = 25
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'

class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image', 'product_count', 'contact']
    search_fields = ['title', 'contact']
    readonly_fields = ['vid']
    list_per_page = 25
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status', 'payment_method', 'oid']
    list_filter = ['paid_status', 'product_status', 'order_date', 'payment_method']
    search_fields = ['user__username', 'oid', 'email', 'phone']
    readonly_fields = ['oid', 'order_date']
    date_hierarchy = 'order_date'
    actions = ['mark_as_paid', 'mark_as_unpaid', 'mark_as_processing', 'mark_as_shipped']
    list_per_page = 25
    ordering = ['-order_date']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(paid_status='paid')
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_unpaid(self, request, queryset):
        queryset.update(paid_status='unpaid')
    mark_as_unpaid.short_description = "Mark selected orders as unpaid"
    
    def mark_as_processing(self, request, queryset):
        queryset.update(product_status='processing')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(product_status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as shipped"

class CartOrderItemAdmin(admin.ModelAdmin):    
    list_display = ['order', 'invoice_no', 'item', 'image', 'qty', 'price', 'total']
    list_filter = ['order__order_date']
    search_fields = ['order__oid', 'invoice_no', 'item__title']
    readonly_fields = ['invoice_no']
    list_per_page = 25

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'review', 'date']
    list_filter = ['rating', 'date']
    search_fields = ['product__title', 'user__username', 'review']
    readonly_fields = ['date']
    list_per_page = 25
    ordering = ['-date']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']
    list_filter = ['date']
    search_fields = ['user__username', 'product__title']
    readonly_fields = ['date']
    list_per_page = 25
    ordering = ['-date']

class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status', 'mobile', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'address', 'mobile']
    readonly_fields = ['aid', 'created_at']
    list_per_page = 25
    ordering = ['-created_at']

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'valid_from', 'valid_to', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['code']
    list_per_page = 25
    ordering = ['-valid_from']

# تسجيل النماذج
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItem, CartOrderItemAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon, CouponAdmin)
