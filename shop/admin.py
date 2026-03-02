from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Slider)
admin.site.register(Banner)
admin.site.register(Contact)
admin.site.register(Basket)
admin.site.register(Likes)
admin.site.register(Comment)

class ProductTypeAdmin(admin.TabularInline):
    model = ProductType
    fk_name = "product"
    extra = 2

class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    fk_name = "product"
    extra = 2

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    inlines = [ProductTypeAdmin,ProductImageAdmin]

admin.site.register(Product, ProductAdmin)
