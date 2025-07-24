from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q

def product_list(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'date_added')
    page_number = request.GET.get('page', 1)

    products = Product.objects.all()

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    
    if sort_by in ['date_added', 'name', 'price']:
        products = products.order_by(sort_by)

    paginator = Paginator(products, 10)  # 10 товаров на страницу
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    subcategories = category.children.all()
    products = category.products.all()
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
    }
    return render(request, 'shop/category_detail.html', context)
