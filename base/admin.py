from django.contrib import admin
from base import models

# Register your models here
admin.site.register(models.MyUser)
admin.site.register(models.Product)
admin.site.register(models.Variant)
admin.site.register(models.Profile)
admin.site.register(models.Order)
admin.site.register(models.Bill)
