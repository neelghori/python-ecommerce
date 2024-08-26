from base.models import Product, Variant
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Product)
def update_product(sender, instance:Product, **kwargs):
    code = str(instance.code)
    
    # According to the first two characters of the code, the material and product type will be updated.
    instance.material = Product.code_reference[code[:2]]['material']
    instance.product_type = Product.code_reference[code[:2]]['type']

@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance:Product, **kwargs):
    # Delete image from db.
    instance.image.delete()
    
@receiver(post_delete, sender=Variant)
def delete_product(sender, instance:Variant, **kwargs):
    # If it is the last variant of the product, delete the product.
    if not Variant.objects.filter(product=instance.product).exists():
        instance.product.delete()
