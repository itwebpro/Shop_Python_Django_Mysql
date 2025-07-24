from django.contrib import admin
from .models import Category, Product, ProductImage
from django.utils.html import mark_safe


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    # существующие настройки
    list_display = ('name', 'category', 'price', 'date_added')
    list_filter = ('category', 'date_added')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
    
    def delete_model(self, request, obj):
        # при удалении товара удаляются и файлы изображений
        for img in obj.images.all():
            img.image.delete(save=False)
        super().delete_model(request, obj)


admin.site.register(Product, ProductAdmin)
