from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

class MyUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True)

class Profile(models.Model):
    user_types = [
        ('customer', 'Customer'),
        ('retailer', 'Retailer')
    ]
    
    user_type = models.CharField(max_length=20, choices=user_types, default='customer')
    
    first_name = models.CharField(max_length=100, null=True, verbose_name='First Name')
    last_name = models.CharField(max_length=100, null=True, verbose_name='Last Name')
    phone = models.CharField(max_length=15, null=True, verbose_name='Phone Number')
    address = models.TextField(null=True, verbose_name='Address')
    transport = models.CharField(max_length=100, null=True, verbose_name='Transport')
    gst = models.CharField(max_length=20, null=True, verbose_name='GST Number')
    city = models.CharField(max_length=50, null=True, verbose_name='City')
    pincode = models.CharField(max_length=10, null=True, verbose_name='Pincode')

    def __str__(self):
        if self.first_name or self.last_name:
            return self.first_name + self.last_name + ' - ' + self.user_type.capitalize()
        else:
            return str(self.id) + ' - ' + self.user_type

class Product(models.Model):
    # Measurement of Aluminium in MM and Zinc in Inch
    code_reference = {
        "10" : {
            "material": "zinc",
            "type": "cabinate handles",
            "measurement": "mm"
        },
        "20" : {
            "material": "zinc",
            "type": "conceal handles",
            "measurement": "mm"
        },
        "30" : {
            "material": "zinc",
            "type": "knobs",
            "measurement": "mm"
        },
        "40" : {
            "material": "zinc",
            "type": "kadi",
            "measurement": "mm"
        },
        "50" : {
            "material": "zinc",
            "type": "mortise handles",
            "measurement": "mm"
        },
        "60" : {
            "material": "aluminium",
            "type": "cabinate handles",
            "measurement": "inch"
        },
        "70" : {
            "material": "aluminium",
            "type": "profile handles",
            "measurement": "inch"
        },
        "80" : {
            "material": "aluminium",
            "type": "conceal handles",
            "measurement": "inch"
        },
        "90" : {
            "material": "aluminium",
            "type": "main door handles",
            "measurement": "inch"
        },
    }
    
    code = models.IntegerField()
    product_type = models.CharField(max_length=20)
    material = models.CharField(max_length=20, default='aluminium')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    def __str__(self):
        return str(self.code)
    
class Variant(models.Model):
    # ('DB Value', 'Display Value')
    size_list_mm = [
        ('96', '96mm'),
        ('128', '128mm'),
        ('160', '160mm'),
        ('224', '224mm'),
        ('256', '256mm'),
        ('288', '288mm'),
        ('416', '416mm'),
        ('576', '576mm'),
        ('864', '864mm'),
        ('1184', '1184mm'),
    ]
    
    size_list_inch = [
        ('4', '4"'),
        ('6', '6"'),
        ('8', '8"'),
        ('10', '10"'),
        ('12', '12"'),
        ('14', '14"'),
        ('16', '16"'),
        ('18', '18"'),
        ('24', '24"'),
        ('36', '36"'),
        ('48', '48"')
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    size_mm = models.CharField(max_length=5, choices=size_list_mm, null=True, blank=True)
    size_inch = models.CharField(max_length=5, choices=size_list_inch, null=True, blank=True)
    
    color_finish_up = models.ForeignKey('Color', on_delete=models.DO_NOTHING, related_name='color_finish_up')
    color_finish_middle = models.ForeignKey('Color', on_delete=models.DO_NOTHING, related_name='color_finish_middle', null=True, blank=True)
    color_finish_down = models.ForeignKey('Color', on_delete=models.DO_NOTHING, related_name='color_finish_down', null=True, blank=True)
    
    price_customer = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    price_retailer = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    
    pieces = models.PositiveIntegerField(default=20)
    
    # For Admin
    minimum_stock = models.PositiveIntegerField(default=0)
    casting_stock = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('product', 'size_mm', 'color_finish_up', 'color_finish_down')
    
    def __str__(self):
        if self.product.material == 'aluminium':
            return f'{self.product.code} - {self.size_inch}'
        else:
            return f'{self.product.code} - {self.size_mm}'

class Color(models.Model):
    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7)
    
    def __str__(self):
        return self.name

class Bill(models.Model):
    status_list = [
        ('placed', 'Placed'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    
    discount = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    
    bill_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default='placed', choices=status_list)

    class Meta:
        ordering = ['-bill_date']
    
    def __str__(self):
        return str(self.id) + ' - ' + self.user.username

class Order(models.Model):
    status_list = [
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ]
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True)

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    cart_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, default='pending', choices=status_list)
    
    tags = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id) + ' - ' + self.user.username
