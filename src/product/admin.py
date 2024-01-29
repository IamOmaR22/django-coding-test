from django.contrib import admin
from .models import Product, Variant, ProductVariant, ProductVariantPrice, ProductImage
# Register your models here.
admin.site.register(Product)
admin.site.register(Variant)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantPrice)
admin.site.register(ProductImage)
