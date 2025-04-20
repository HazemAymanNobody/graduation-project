from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404 , redirect
from taggit.models import Tag
from core.models import Product , Category , Vendor , CartOrder , CartOrderItem, ProductImages , ProductReview , Wishlist , Address, Coupon
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from django.core import serializers
from shortuuid.django_fields import ShortUUIDField

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm                                                                                                                           

import calendar
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

import stripe
import json

# Create your views here.
def index(request):
    # products = product.objects.all().order_by('-id')
    products = Product.objects.filter(product_status='published', featured=True)
    categories = Category.objects.all()
    
    wishlist = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user)
    
    context = {
        'products': products,
        'categories': categories,
        'wishlist': wishlist,
    }

    return render(request, 'core/index.html', context) 


def product_list_view(request):
    products = Product.objects.filter( product_status='published')

    context = {
        'products' : products,
    }
    return render(request, 'core/product-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()
    # categories = category.objects.all().annotate(product_count=Count('product'))

    context = {
        'categories' : categories,
    }
    return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status='published', category=category)

    context = {
        'category' :category,
        'products' :products,
    }
    return render(request, 'core/category-product-list.html', context)






def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        'vendors' : vendors,
    }
    return render(request, 'core/vendor-list.html', context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status='published')
    context = {
        'vendor' : vendor,
        'products' : products
    }
    return render(request, 'core/vendor-detail.html', context)



def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # Getting all reviews related to a product 
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # Getting average reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Product Review form
    review_form = ProductReviewForm()

    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False


    p_image = product.p_images.all()
    
    context = {
        "p":product,
        "make_review": make_review,
        "review_form": review_form,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "products": products,
    }
    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status='published').order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag,
    }

    return render(request, "core/tag.html", context)



def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'average_reviews': average_reviews
        }
    )



def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")
    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)



def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    
    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

     
    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)


    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])]  = {
        'title': request.GET['title'],
        'qty':  request.GET['qty'],
        'price':  request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }  
    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product

    return JsonResponse({"data": request.session['cart_data_obj'], "totalcartitems": len(request.session['cart_data_obj'])})



@login_required
def cart_view(request):
    cart_total_amount = 0
    try:
        if 'cart_data_obj' in request.session:
            # Calculate total amount
            for p_id, item in request.session['cart_data_obj'].items():
                # Convert string values to proper numeric types
                qty = int(item['qty'])
                price = float(item['price'])
                cart_total_amount += qty * price
            
            if request.method == "POST":
                print("Form submitted, creating order...")
                # Create order
                order = CartOrder.objects.create(
                    user=request.user,
                    price=cart_total_amount,
                )
                
                # Ensure oid is set
                if not order.oid:
                    order.oid = ShortUUIDField(length=5, max_length=20, alphabet="1234567890").generate()
                    order.save()
                
                print(f"Order created with ID: {order.oid}")
                
                # Create order items
                for p_id, item in request.session['cart_data_obj'].items():
                    # Convert string values to proper numeric types
                    qty = int(item['qty'])
                    price = float(item['price'])
                    CartOrderItem.objects.create(
                        order=order,
                        invoice_no="INVOICE_NO-" + str(order.id),
                        item=item['title'],
                        image=item['image'],
                        qty=qty,
                        price=price,
                        total=qty * price
                    )
                print("Order items created")
                
                # Clear the cart
                del request.session['cart_data_obj']
                messages.success(request, "Your order has been placed successfully!")
                print(f"Redirecting to checkout with order ID: {order.oid}")
                return redirect('core:checkout', oid=order.oid)
    except ValueError as e:
        print(f"Error in cart_view - Invalid number format: {str(e)}")
        messages.error(request, "Invalid price or quantity format in cart")
    except Exception as e:
        print(f"Error in cart_view: {str(e)}")
        messages.error(request, f"Error processing your order: {str(e)}")
    
    context = {
        "cart_data": request.session.get('cart_data_obj', {}),
        "totalcartitems": len(request.session.get('cart_data_obj', {})),
        "cart_total_amount": cart_total_amount,
    }
    return render(request, 'core/cart.html', context)



def delete_item_from_cart(request):  
    product_id = str(request.GET['id'])  
    if 'cart_data_obj' in request.session:  
        if product_id in request.session['cart_data_obj']:  
            cart_data = request.session['cart_data_obj']  
            del request.session['cart_data_obj'][product_id]  
            request.session['cart_data_obj'] = cart_data  
    
    cart_total_amount = 0  
    if 'cart_data_obj' in request.session:  
        for pid, item in request.session['cart_data_obj'].items():  
            cart_total_amount += int(item['qty']) * float(item['price'])  
    
    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], "totalcartitems": len(request.session['cart_data_obj']) , 'cart_total_amount':cart_total_amount } )  
    return JsonResponse({ "data":context , 'totalcartitems':len(request.session['cart_data_obj']) })



def update_cart(request):  
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty'] 
    #product_qty = request.GET.get('qty') 

    if 'cart_data_obj' in request.session:  
        if product_id in request.session['cart_data_obj']:  
            cart_data = request.session['cart_data_obj']  
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data  
            

    cart_total_amount = 0  
    if 'cart_data_obj' in request.session:  
        for pid, item in request.session['cart_data_obj'].items():  
            cart_total_amount += int(item['qty']) * float(item['price'])  
    
    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], "totalcartitems": len(request.session['cart_data_obj']) , 'cart_total_amount':cart_total_amount } )  
    return JsonResponse({ "data":context , 'totalcartitems':len(request.session['cart_data_obj']) })


@login_required
def save_checkout_info(request):
    if request.method == "POST":
        try:
            order_id = request.POST.get("order_id")
            order = CartOrder.objects.get(oid=order_id, user=request.user)
            
            # Update order information
            order.full_name = request.POST.get("full_name")
            order.email = request.POST.get("email")
            order.phone = request.POST.get("mobile")
            order.address = request.POST.get("address")
            order.city = request.POST.get("city")
            order.state = request.POST.get("state")
            order.country = request.POST.get("country")
            order.save()
            
            messages.success(request, "Order information saved successfully!")
            return redirect("core:payment-completed", oid=order.oid)
            
        except CartOrder.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("core:cart")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("core:cart")
            
    return redirect("core:cart")

@login_required
def checkout(request, oid):
    try:
        order = CartOrder.objects.get(oid=oid, user=request.user)
        order_items = CartOrderItem.objects.filter(order=order)
        
        context = {
            "order": order,
            "order_items": order_items,
        }
        return render(request, 'core/checkout.html', context)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('core:cart')
    except Exception as e:
        messages.error(request, f"Error accessing checkout: {str(e)}")
        return redirect('core:cart')

@csrf_exempt
def creat_checkout_session(request, oid):
    try:
        order = CartOrder.objects.get(oid=oid)
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
            
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Order {order.oid}',
                    },
                    'unit_amount': int(order.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('core:payment-completed', args=[order.oid])),
            cancel_url=request.build_absolute_uri(reverse('core:payment-failed')),
            customer_email=email,
            metadata={
                'order_id': order.oid,
                'user_id': order.user.id,
            }
        )
        
        return JsonResponse({'sessionId': session.id})
        
    except CartOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def validate_coupon(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'valid': False, 'message': 'Coupon code is required'})
            
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                return JsonResponse({
                    'valid': True,
                    'discount': coupon.discount,
                    'message': 'Coupon applied successfully'
                })
            else:
                return JsonResponse({
                    'valid': False,
                    'message': 'Coupon has expired'
                })
        except Coupon.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid coupon code'
            })
            
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': str(e)
        })

@login_required
def payment_completed_view(request, oid):
    try:
        order = CartOrder.objects.get(oid=oid, user=request.user)
        order.paid_status = 'paid'
        order.product_status = 'processing'
        order.save()
        
        # Clear cart items
        CartOrderItem.objects.filter(order=order).delete()
        
        messages.success(request, "Payment completed successfully!")
        return render(request, 'core/payment-completed.html', {'order': order})
        
    except CartOrder.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('core:index')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('core:index')

@login_required
def payment_failed_view(request):
    messages.error(request, "Payment failed. Please try again.")
    return render(request, 'core/payment-failed.html')

@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    addresses = Address.objects.filter(user=request.user)

    # Get order statistics
    orders = (
        CartOrder.objects.filter(user=request.user)
        .annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(count=Count("id"))
        .values("month", "count")
    )
    month = []
    total_orders = []

    for i in orders:
        month.append(calendar.month_name[i['month']])
        total_orders.append(i["count"])

    # Handle new address creation
    if request.method == "POST":
        address_text = request.POST.get("address")
        mobile = request.POST.get("mobile")

        if not address_text or not mobile:
            messages.error(request, "Both address and mobile number are required.")
            return redirect("core:dashboard")

        # Check if the exact same address already exists
        if not Address.objects.filter(user=request.user, address=address_text, mobile=mobile).exists():
            # Set all other addresses as non-default if this is the first address
            if not addresses.exists():
                is_default = True
            else:
                is_default = False

            Address.objects.create(
                user=request.user,
                address=address_text,
                mobile=mobile,
                is_default=is_default
            )
            messages.success(request, "Address added successfully.")
        else:
            messages.warning(request, "This address already exists.")

        return redirect("core:dashboard")

    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None
        messages.warning(request, "Please complete your profile information.")

    context = {
        "user_profile": user_profile,
        "orders_list": orders_list,
        "addresses": addresses,
        "orders": orders,
        "month": month,
        "total_orders": total_orders,
    }
    return render(request, 'core/dashboard.html', context)



def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItem.objects.filter(order=order)
    context = {
        "order_items": order_items
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET["id"]
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})




@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.all()
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)


def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)

    context = {}

    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = Wishlist.objects.create(
            product=product,
            user=request.user
        )
        context = {
            "bool": True
        }

    return JsonResponse(context)



def remove_wishlist(request):
        pid = request.GET['id']
        wishlist = Wishlist.objects.filter(user=request.user)

        product = Wishlist.objects.get(id=pid)
        product.delete()

        context = {
            "bool": True,
            "w":wishlist
        }
        wishlist_json = serializers.serialize('json', wishlist)

        data = render_to_string("core/async/wishlist-list.html", context)
        return JsonResponse({"data": data, "w":wishlist_json})    



# Other pages
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email'] 
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name = full_name,
        email = email,
        phone = phone,
        subject = subject,
        message = message,
    )

    data = {
        "bool": True,
        "message": "Message sent successfully"
    }
    return JsonResponse({"data":data})



def about_us(request):
    return render(request, "core/about_us.html")


def purchase_guide(request):
    return render(request, "core/purchase_guide.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def terms_of_service(request):
    return render(request, "core/terms_of_service.html")


def order_tracking(request):
    if not request.user.is_authenticated:
        return redirect('userauths:sign-in')
    
    orders = CartOrder.objects.filter(user=request.user).order_by('-date')
    context = {
        'orders': orders,
    }
    return render(request, 'core/order-tracking.html', context)

def settings_view(request):
    if not request.user.is_authenticated:
        return redirect('userauths:sign-in')
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Update user profile
        request.user.email = email
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.phone = phone
        request.user.address = address
        
        # Handle password change if provided
        if current_password and new_password and confirm_password:
            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                else:
                    messages.error(request, 'New passwords do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        try:
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
        
        return redirect('core:settings')
    
    context = {
        'user': request.user,
    }
    return render(request, 'core/settings.html', context)













