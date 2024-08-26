from django.forms import ModelForm
from base.models import Product, Variant, Profile

class ProductForm(ModelForm):
    # Remove the colon from the label
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ProductForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Product
        fields = '__all__'
        
class VariantForm(ModelForm):
    # Remove the colon from the label
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VariantForm, self).__init__(*args, **kwargs)
            
    class Meta:
        model = Variant
        exclude = ['product']
        

class CustomerForm(ModelForm):
    # Remove the colon from the label
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(CustomerForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Profile
        exclude = ['user_type', 'gst', 'transport']

class RetailerForm(ModelForm):
    # Remove the colon from the label
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(RetailerForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Profile
        exclude = ['user_type']
