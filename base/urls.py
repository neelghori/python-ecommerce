from django.urls import path
from base import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('user-register/', views.user_register, name='user-register'),
    path('user-delete/<str:pk>/', views.user_delete, name='user-delete'),
    path('user-signin/', views.user_signin, name='user-signin'),
    path('user-signup/', views.user_signup, name='user-signup'),
    path('user-signout/', views.user_signout, name='user-signout'),
    
    path('create-profile/', views.create_profile, name='create-profile'),
    
    path('admin-data/', views.admin_data, name='admin-data'),
    path('admin-settings/', views.admin_settings, name='admin-settings'),

    path('product-types/', views.variant_types, name='product-types'),
    path('products/<str:ptype>', views.variants, name='products'),
    path('handle/<str:pk>/', views.variant, name='handle'),
    path('create-variant/', views.create_bulk_variants, name='create-variant'),
    path('create-bulk-variants/', views.create_bulk_variants, name='create-bulk-variants'),
    path('update-variant/<str:pk>/', views.update_variant, name='update-variant'),
    path('delete-handle/<str:pk>/', views.delete_handle, name='delete-handle'),
    
    path('get-price/', views.get_price, name='get-price'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    
    path('colors/', views.colors, name='colors'),
    path('delete-color/<str:pk>/', views.delete_color, name='delete-color'),
    
    path('cart/', views.cart, name='cart'),
    path('place-order/', views.place_order, name='place-order'),
    path('remove-cart-item/<str:pk>/', views.remove_cart_item, name='remove-cart-item'),
    
    path('orders/', views.orders, name='orders'),
    
    path('bill/<str:pk>/', views.bill, name='bill'),
    path('order-details/<str:pk>/', views.user_bill, name='user-bill'),
    path('toggle_order_status/', views.toggle_order_status, name='toggle_order_status'),
    path('update_bill_status/', views.update_bill_status, name='update_bill_status'),
    path('delete-bill/<str:pk>/', views.delete_bill, name='delete-bill'),
    
    # Miscellanous
    path('create-dummy-orders/', views.create_dummy_orders, name='create-dummy-orders'),
]
