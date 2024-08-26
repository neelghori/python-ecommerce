from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from base.decorators import check_access
from base.models import MyUser, Profile, Product, Variant, Color, Order, Bill
from base.forms import ProductForm, VariantForm, CustomerForm, RetailerForm

import json
import random

@check_access(feature='home')
def home(request):
    context = {}
    return render(request, 'base/home.html', context)


@check_access(admin_only=True)
def user_register(request):    
    if request.user.is_superuser:
        users = MyUser.objects.all()
        
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirmPassword')
            
            user_model = get_user_model()

            if user_model.objects.filter(username__iexact=username).exists() == True:
                messages.error(request, 'Username is already taken. Try a differenct username.')

            elif password != confirmPassword:
                messages.error(request, f'Passwords do not match.')

            elif password == '':
                messages.error(request, f'Password cannot be empty. {request.POST.get("password")})')

            else:
                user = MyUser.objects.create_user(username=username, email=email, password=password)

                user_type = 'retailer'

                # Create a profile
                profile = Profile.objects.create(user_type=user_type)
                
                # Attach the profile to the user
                user.user_profile = profile
                user.save()
                
                messages.success(request, 'User created successfully.')
                    
                return redirect('user-register')
        
        context = {'users':users}
        return render(request, 'base/user_register.html', context)

    else:
        messages.error(request, 'You do not have permission to access this page.')
        
        return redirect('home')

@check_access(admin_only=True)
def user_delete(request, pk):
    user = MyUser.objects.get(id=pk)
    if user.username == 'admin':
        messages.error(request, 'Beta limit ma.')
        
        return redirect('user-register')
    
    if request.method == 'POST':
        user.delete()
        
        return redirect('user-register')
    
    context = {'delete_object_type': 'User', 'delete_object_value': user.username}
    return render(request, 'base/delete.html', context)

def user_signin(request):
    if request.user.is_authenticated:
        return redirect('product-types')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            return redirect('home')
        
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'base/user_signin.html')

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('product-types')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        
        user_model = get_user_model()
        
        if user_model.objects.filter(username__iexact=username).exists() == True:
            messages.error(request, 'Username is already taken. Try a differenct username.')
        
        elif password != confirmPassword:
            messages.error(request, f'Passwords do not match.')
        
        elif password == '':
            messages.error(request, f'Password cannot be empty. {request.POST.get("password")})')
        
        else:
            user = MyUser.objects.create_user(username=username, email=email, password=password)
            
            user_type = 'customer'
            
            # Create a profile
            profile = Profile.objects.create(user_type=user_type)
            
            # Attach the profile to the user
            user.user_profile = profile
            user.save()
            
            messages.success(request, 'User created successfully.')
                
            return redirect('user-signin')
    
    return render(request, 'base/user_signup.html')

def user_signout(request):
    logout(request)
    
    return redirect('home')


@check_access(feature='create-profile')
def create_profile(request):
    if request.user.user_profile.user_type == 'retailer':
        form = RetailerForm(instance=request.user.user_profile)
        
    # elif request.user.user_profile.user_type == 'customer':
    elif request.user.user_profile.user_type == 'customer':
        form = CustomerForm(instance=request.user.user_profile)
    
    if request.method == 'POST':
        if request.user.user_profile.user_type == 'retailer':
            form = RetailerForm(request.POST, instance=request.user.user_profile)
            
        elif request.user.user_profile.user_type == 'customer':
            form = CustomerForm(request.POST, instance=request.user.user_profile)
        
        if form.is_valid():
            form.save()
            
            return redirect('product-types')
    
    context = {'form': form}
    return render(request, 'base/create_profile.html', context)


@check_access(admin_only=True)
def admin_data(request):
    handles = Variant.objects.all()
    orders = Order.objects.all()
    order_statuses = ['In-Cart', 'Placed', 'Confirmed', 'Shipped', 'Delivered']
    bills = Bill.objects.all()

    ####################
    # Retailer Analytics
    ####################
    
    # Get top 5 selling products by quantity (delivered)
    top_5_ret_quant = Order.objects.filter(status='delivered', user__user_profile__user_type='retailer').values('variant__product__code').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    
    # Get top 5 selling products by revenue (delivered)
    top_5_ret_rev = Order.objects.filter(status='delivered', user__user_profile__user_type='retailer').values('variant__product__code').annotate(total_revenue=Sum('quantity') * Sum('variant__price_retailer')).order_by('-total_revenue')[:5]
    
    # Get order stats for orders placed by retailers
    retailer_order_stats = Order.objects.filter(user__user_profile__user_type='retailer').values('status').annotate(total=Sum('quantity')).order_by('status')


    ####################
    # Customer Analytics
    ####################

    # # Get top 5 selling products by quantity (delivered)
    # top_5_cust_quant = Order.objects.filter(status='delivered', user__user_profile__user_type='customer').values('variant__product__code').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    
    # # Get top 5 selling products by revenue (delivered)
    # top_5_cust_rev = Order.objects.filter(status='delivered', user__user_profile__user_type='customer').values('variant__product__code').annotate(total_revenue=Sum('quantity') * Sum('variant__price_customer')).order_by('-total_revenue')[:5]
    
    # # Get order stats for orders placed by customers
    # customer_order_stats = Order.objects.filter(user__user_profile__user_type='customer').values('status').annotate(total=Sum('quantity')).order_by('status')

    graph_data = {
        'orders_per_month': {
            'labels': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            'data': [
                orders.filter(order_date__month=1).count(),
                orders.filter(order_date__month=2).count(),
                orders.filter(order_date__month=3).count(),
                orders.filter(order_date__month=4).count(),
                orders.filter(order_date__month=5).count(),
                orders.filter(order_date__month=6).count(),
                orders.filter(order_date__month=7).count(),
                orders.filter(order_date__month=8).count(),
                orders.filter(order_date__month=9).count(),
                orders.filter(order_date__month=10).count(),
                orders.filter(order_date__month=11).count(),
                orders.filter(order_date__month=12).count()
            ]
        },
        'order_stats': {
            'labels': order_statuses,
            'data': [
                orders.filter(status='in-cart').count(),
                orders.filter(status='placed').count(),
                orders.filter(status='confirmed').count(),
                orders.filter(status='shipped').count(),
                orders.filter(status='delivered').count()
            ]
        },
        
        # Retailer Stats
        'top_5_ret_quant' : {
            'labels': [item['variant__product__code'] for item in top_5_ret_quant],
            'data': [item['total_quantity'] for item in top_5_ret_quant]
        },
        'top_5_ret_rev' : {
            'labels': [item['variant__product__code'] for item in top_5_ret_rev],
            'data': [item['total_revenue'] for item in top_5_ret_rev]
        },
        'retailer_order_stats' : {
            'labels': order_statuses,
            'data': [item['total'] for item in retailer_order_stats]
        }
    }
    
    # Dummy Graph Data
    dummy_graph_data = {
        "orders_per_month": {
            "labels": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            "data": [random.randint(0, 100) for i in range(12)]
        },
        "order_stats": {
            "labels": ["In-Cart", "Placed", "Confirmed", "Shipped", "Delivered"],
            "data": [random.randint(0, 100) for i in range(5)]
        },
        "top_5_ret_quant": {
            "labels": ["101", "107", "109", "110", "209"],
            "data": [random.randint(0, 100) for i in range(5)]
        },
        "top_5_ret_rev": {
            "labels": ["101", "107", "109", "110", "209"],
            "data": [random.randint(0, 100) for i in range(5)]
        },
        "retailer_order_stats": {
            "labels": ["In-Cart", "Placed", "Confirmed", "Shipped", "Delivered"],
            "data": [random.randint(0, 100) for i in range(5)]
        }
    }

    context = {'handles': handles, 'bills': bills, 'graph_data': graph_data}
    return render(request, 'base/admin_data.html', context)

@check_access(admin_only=True)
def admin_settings(request):
    return render(request, 'base/admin_settings.html')

@check_access()
def variant(request, pk):
    product = Product.objects.get(id=pk)
    distinct_finish_up_values = Variant.objects.filter(product=product).values_list('color_finish_up', flat=True).distinct()
    distinct_finish_middle_values = Variant.objects.filter(product=product).values_list('color_finish_middle', flat=True).distinct()
    distinct_finish_down_values = Variant.objects.filter(product=product).values_list('color_finish_down', flat=True).distinct()
    
    # Get unique color combinations
    variants = []
    
    for finish_up in distinct_finish_up_values:
        if distinct_finish_down_values:
            for finish_down in distinct_finish_down_values:
                if distinct_finish_middle_values:
                    for finish_middle in distinct_finish_middle_values:
                        variant = Variant.objects.filter(product=product, color_finish_up=finish_up, color_finish_middle=finish_middle, color_finish_down=finish_down).first()

                        if variant:
                            variants.append(variant)
                else:
                    variant = Variant.objects.filter(product=product, color_finish_up=finish_up, color_finish_down=finish_down).first()

                    if variant:
                        variants.append(variant)
        else:
            variant = Variant.objects.filter(product=product, color_finish_up=finish_up).first()
            variants.append(variant)
    
    # Sort variants by size
    if product.material == 'aluminium':
        variants = sorted(variants, key=lambda x: int(x.size_inch))

        # Get all the sizes with the same color combination
        sizes = Variant.objects.filter(product=product, color_finish_up=variants[0].color_finish_up, color_finish_down=variants[0].color_finish_down).values_list('size_inch', flat=True).distinct()
        
        sizes = sorted(sizes, key=lambda x: int(x))

    elif product.material == 'zinc':
        variants = sorted(variants, key=lambda x: int(x.size_mm))
        
        # Get all the sizes with the same color combination
        sizes = Variant.objects.filter(product=product, color_finish_up=variants[0].color_finish_up, color_finish_down=variants[0].color_finish_down).values_list('size_mm', flat=True).distinct()
        
        sizes = sorted(sizes, key=lambda x: int(x))
    
    context = {'product': product, 'variants': variants, 'sizes': sizes}
    return render(request, 'base/variant.html', context)

@check_access(feature='handles-page')
def variant_types(request):
    product_types = []
    for key, pref in Product.code_reference.items():
        ptype = pref.get('type')
        pmaterial = pref.get('material')
        pimage = f"{pmaterial}-{ptype.replace(' ', '-')}.png"
        
        product_types.append(
            (
                ptype,
                pmaterial,
                pimage
            )
        )

    context = {'product_types': product_types}
    return render(request, 'base/variant_types.html', context)

@check_access(feature='handles-page')
def variants(request, ptype:str):
    products = Product.objects.filter(product_type=ptype.lower())
    
    # Add a price_retailer and price_customer field such that it is the lowest of the variants' price
    for product in products:
        variants = Variant.objects.filter(product=product)
        product.price_retailer = min([variant.price_retailer for variant in variants])
        product.price_customer = min([variant.price_customer for variant in variants])
    
    context = {'products': products, 'ptype': ptype.title()}
    return render(request, 'base/variants.html', context)

@check_access(admin_only=True)
def create_variant(request):
    form = VariantForm()
    
    if request.method == 'POST':
        product_code = request.POST.get('product_code')
        form = VariantForm(request.POST, request.FILES)
        
        # Get or create the product
        product, created = Product.objects.get_or_create(code=int(product_code))
        
        # Attach the product to the variant
        form.instance.product = product
        
        if form.is_valid():
            instance:Variant = form.save(commit=False)
            # Image is now attached to product.
            # instance.image.name = f'{instance.product.code}.{instance.image.name.split(".")[-1]}'
            instance.save()
            
            return redirect('product-types')
    
    context = {'form': form}
    return render(request, 'base/create_variant.html', context)

@check_access(admin_only=True)
def create_bulk_variants(request):
    codes = ['10', '20', '30', '40', '50', '60', '70', '80', '90']
    sizes_mm = [size[0] for size in Variant.size_list_mm]
    sizes_inch = [size[0] for size in Variant.size_list_inch]
    colors = Color.objects.all()
    
    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('product-image')
        
        if not image:
            messages.error(request, 'Please upload an image.')
            return redirect('create-bulk-variants')
        
        # Product Code Series
        if data.get('code-initials'):
            product_code = int(data.get('code-initials'))
            code_initials = int(data.get('code-initials')[:2])
        else:
            messages.error(request, 'Please enter the product code.')
            return redirect('create-bulk-variants')
        
        if int(code_initials) > 55:
            size_list = data.getlist('sizes_inches')
        else:
            size_list = data.getlist('sizes_mm')
        
        colors_finish_up = data.getlist('color1[]')
        colors_finish_middle = data.getlist('color2[]')
        colors_finish_down = data.getlist('color3[]')
        
        product, created = Product.objects.get_or_create(code=product_code)
        # Attach the image to the product and rename it
        product.image = image
        product.image.name = f'{product.code}.{image.name.split(".")[-1]}'
        product.save()
        
        for size in size_list:
            for i in range(len(colors_finish_up)):
                color_finish_up = Color.objects.get(id=colors_finish_up[i])

                if colors_finish_middle[i] == 'none':
                    color_finish_middle = None
                else:
                    color_finish_middle = Color.objects.get(id=colors_finish_middle[i])

                if colors_finish_down[i] == 'none':
                    color_finish_down = None
                else:
                    color_finish_down = Color.objects.get(id=colors_finish_down[i])
                
                if product.material == 'zinc':
                    Variant.objects.create(product=product, size_mm=size, color_finish_up=color_finish_up, color_finish_middle=color_finish_middle, color_finish_down=color_finish_down)
                else:
                    Variant.objects.create(product=product, size_inch=size, color_finish_up=color_finish_up, color_finish_middle=color_finish_middle, color_finish_down=color_finish_down)
    
        messages.success(request, 'Products and Variants created successfully.')
    
    context = {'codes':codes, 'sizes_mm': sizes_mm, 'sizes_inch': sizes_inch, 'colors': colors}
    return render(request, 'base/create_bulk_variants.html', context)

@check_access(admin_only=True)
def update_variant(request, pk):
    variant = Variant.objects.get(id=pk)
    form = VariantForm(instance=variant)
    
    if request.method == 'POST':
        product_image = request.FILES.get('product-image')
        product_code = request.POST.get('product-code')
        form = VariantForm(request.POST, instance=variant)
        
        if form.is_valid():
            instance:Variant = form.save(commit=False)
            
            # If product image is uploaded then update the image
            if product_image:
                product = variant.product
                product.image = product_image
                product.image.name = f'{product.code}.{product_image.name.split(".")[-1]}' # Rename the image file
                product.save()
            
            # Check if new product code is provided
            if product_code != variant.product.code:
                # Get or create the product
                product, created = Product.objects.get_or_create(code=int(product_code))
                
                # Attach the product to the variant
                instance.product = product
            
            # Check if the variant is unique
            if Variant.objects.filter(product=instance.product, size_mm=variant.size_mm, size_inch=instance.size_inch, color_finish_up=instance.color_finish_up, color_finish_middle=instance.color_finish_down, color_finish_down=instance.color_finish_down).exclude(id=instance.id).exists():
                messages.error(request, 'Variant already exists.')
                
                return redirect('update-variant', pk=variant.id)
            
            try:
                instance.save()
            except IntegrityError as e:
                messages.error(request, 'Variant already exists.')
            
            return redirect('update-variant', pk=variant.id)
    
    context = {'form': form, 'variant': variant}
    return render(request, 'base/update_variant.html', context)

@check_access(admin_only=True)
def delete_handle(request, pk):
    handle = Variant.objects.get(id=pk)
    
    if request.method == 'POST':
        handle.delete()
        
        return redirect('admin-data')
    
    context = {'delete_object_type': 'Handle', 'delete_object_value': handle.product.code}
    return render(request, 'base/delete.html', context)


@check_access(admin_only=True)
def colors(request):
    colors = Color.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name').capitalize()
        hex_code = request.POST.get('hex_code')

        Color.objects.create(name=name, hex_code=hex_code)

        return redirect('colors')
    
    context = {'colors': colors}
    return render(request, 'base/color.html', context)

@check_access(admin_only=True)
def delete_color(request, pk):
    color = Color.objects.get(id=pk)
    
    if request.method == 'POST':
        color.delete()
        
        return redirect('colors')
    
    context = {'delete_object_type': 'Color', 'delete_object_value': color.name}
    return render(request, 'base/delete.html', context)


@check_access(allowed_users=['retailer'])
def cart(request):
    orders = Order.objects.filter(user=request.user, status='pending', bill=None, delivery_date=None)
    
    context = {'orders': orders}
    return render(request, 'base/cart.html', context)

@check_access(allowed_users=['retailer'])
def add_to_cart(request):
    pk = json.loads(request.body.decode('utf-8'))['var_id']
    
    variant = Variant.objects.get(id=pk)

    already_exists = Order.objects.filter(user=request.user, variant=variant, status='pending', delivery_date=None, bill=None, quantity=1).exists()
    
    if already_exists:
        return JsonResponse({"status": "already_exists"})
    
    Order.objects.create(user=request.user, variant=variant)
    
    messages.success(request, 'Item added to cart.')
    
    return JsonResponse({"status": "success"})

@check_access(allowed_users=['retailer'])
def remove_cart_item(request, pk):
    order = Order.objects.get(id=pk)
    
    if order.user != request.user and request.user.user_profile.user_type != 'retailer':
        messages.error(request, 'You do not have permission to delete this item.')
        
        return redirect('cart')
    
    order.delete()
    
    return redirect('cart')

@check_access(allowed_users=['retailer'])
def place_order(request):
    data = json.loads(request.body.decode('utf-8'))
    variant_ids = data['itemIds']
    quantities = [int(quantity) for quantity in data['quantities']]
    
    # Generate a Bill
    bill = Bill.objects.create(user=request.user)
    total_amount = 0
    
    for i in range(len(variant_ids)):
        # Get the order with variant id and in-cart status
        order = Order.objects.filter(user=request.user, variant_id=variant_ids[i], status='pending', bill=None, delivery_date=None).first()
        
        # Update the bill
        order.bill = bill
        
        # Modify the quantity
        order.quantity = quantities[i]
        
        # Add Order Date
        order.order_date = timezone.now()
        
        # Save the order
        order.save()
        
        total_amount += order.variant.price_retailer * order.quantity
    
    bill.total = total_amount
    bill.save()
    
    messages.success(request, 'Order placed successfully!')
    
    return JsonResponse({'status': 'success', 'redirect_url': reverse('orders')})


@check_access(allowed_users=['retailer'])
def orders(request):
    bills = Bill.objects.filter(user=request.user)
    
    context = {'bills': bills}
    return render(request, 'base/orders.html', context)

@check_access(allowed_users=['retailer'])
def user_bill(request, pk):
    bill = Bill.objects.get(id=pk)
    
    context = {'bill': bill}
    return render(request, 'base/user_bill.html', context)

@check_access(admin_only=True)
def bill(request, pk):
    bill = Bill.objects.get(id=pk)
    
    context = {'bill': bill}
    return render(request, 'base/bill.html', context)

@check_access(admin_only=True)
def toggle_order_status(request):
    order_id = request.GET.get('order_id')
    new_status = request.GET.get('new_status')
    
    # Update the order status in your database
    order = Order.objects.get(id=order_id)
    order.status = new_status
    order.save()
    
    # Return a JSON response
    return JsonResponse({'success': True})

@check_access(admin_only=True)
def update_bill_status(request):
    data = json.loads(request.body)
    bill_id = data.get('bill_id')
    new_status = data.get('new_status')

    try:
        bill = Bill.objects.get(id=bill_id)
        if new_status in dict(Bill.status_list):
            bill.status = new_status
            bill.save()
            print(f"Bill status updated to {new_status}")
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
    except Bill.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bill not found'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@check_access(admin_only=True)
def delete_bill(request, pk):
    bill = Bill.objects.get(id=pk)
    
    if request.method == 'POST':
        bill.delete()
        
        return redirect('admin-data')
    
    context = {'delete_object_type': 'Bill', 'delete_object_value': bill.id}
    return render(request, 'base/delete.html', context)

# ================
# Helper Functions
# ================
@check_access(allowed_users=['retailer'])
def get_price_old(request):
    data = json.loads(request.body.decode('utf-8'))
    var_id = data['var_id']
    size = data['size'].replace(' mm', '')
    
    variant = Variant.objects.get(id=var_id)
    
    if variant.size_mm != size:
        size_variant = Variant.objects.filter(product=variant.product, color_finish_up=variant.color_finish_up, color_finish_down=variant.color_finish_down, size_mm=size)

        if size_variant.exists():
            variant = variant.first()
            exists = True
            print('Variant exists.')
        else:
            exists = False
            existing_size = variant.size_mm + ' mm'
            messages.error(request, 'Variant does not exist.')
            print('Variant does not exist.')
    else:
        exists = True

    price = variant.price_retailer
    
    return JsonResponse({ 'var_id': variant.id, 'price': price, 'exists': exists, 'existing_size': existing_size})

@check_access(allowed_users=['retailer'])
def get_price(request):
    data = json.loads(request.body.decode('utf-8'))
    var_id = data['var_id']
    size = data['size']
    
    variant = Variant.objects.get(id=var_id)
    
    variants = Variant.objects.filter(product=variant.product, color_finish_up=variant.color_finish_up, color_finish_middle=variant.color_finish_middle, color_finish_down=variant.color_finish_down)
    if variant.product.material == 'zinc':
        variants_by_sizes = sorted(variants, key=lambda x: int(x.size_mm))
    else:
        variants_by_sizes = sorted(variants, key=lambda x: int(x.size_inch))
    
    if size != None:
        if variant.product.material == 'zinc':
            variant = variants.filter(size_mm=size).first()
        else:
            variant = variants.filter(size_inch=size).first()
    else:
        # Get the price of the variant with lowest size converting size to int  
        variant = variants_by_sizes[0]
    
    # Get all the sizes in order
    if variant.product.material == 'zinc':
        sizes = [variant.size_mm for variant in variants_by_sizes]
    else:
        sizes = [variant.size_inch for variant in variants_by_sizes]
    
    # Get the price for the selected variant
    price = variant.price_retailer
    
    return JsonResponse({ 'var_id': variant.id, 'price': price, 'sizes': list(sizes) })

@check_access(admin_only=True)
def create_dummy_orders(request):
    # Create random dummy orders with different statuses
    for i in range(50):
        print(i, end=" ")
        variant = Variant.objects.all().order_by('?').first()
        user = MyUser.objects.all().order_by('?').first()
        
        status = random.choice(['in-cart', 'placed', 'confirmed', 'shipped', 'delivered'])
        
        # Random date within this year
        created_date = timezone.now() - timezone.timedelta(days=random.randint(1, 365))
        # Date after a few days or weeks of the order date
        order_date = created_date + timezone.timedelta(days=random.randint(1, 60))
        
        Order.objects.create(user=user, variant=variant, status=status, quantity=random.randint(1, 10), cart_date=created_date, order_date=order_date)
    
    return redirect('admin-data')
