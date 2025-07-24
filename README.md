Пример создания на python + django и базой данных mysql основы каталога товаров и админ панели. Основная функциональность: 1) админ панель: вход по паролю админа. добавление, редактирование, удаление категорий товаров, категориии должны выводится в виде дерева в неограниченном количестве подкатегорий. добавление, редактирование, удаление товаров. форма для товаров: название, описание, цена, категория, фото товара (до 10 штук фото файлов, предусмотреть при удалении товара, также удаление файлов фото товара). 2) пользовательная часть: вывод товаров по-странично, сортировка по дате добавления, названию, цене. форма поиска по названию и описанию. Переход на отдельную страницу товара с подробным описанием и выводом всех параметров (название, описание, цена, категории ввиде цепочки ссылок если категории имеет родительные категории)

### 1. Установка и настройка проекта

**Шаги:**

1. Создайте виртуальное окружение и активируйте его.
2. Установите Django и mysqlclient:
```bash
pip install django mysqlclient
```
3. Создайте проект:
```bash
django-admin startproject catalog_project
cd catalog_project
```
4. Создайте приложение:
```bash
python manage.py startapp shop
```
5. Настройте `settings.py` для использования MySQL и добавьте ваше приложение `shop` в `INSTALLED_APPS`.

---

### 2. Настройка `settings.py`

```python
# catalog_project/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

INSTALLED_APPS = [
    # другие приложения
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',  # наше приложение
]
```

---

### 3. Модели (`shop/models.py`)

```python
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[str(self.id)])

    def get_ancestors(self):
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        return ancestors

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.id)])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
```

---

### 4. Миграции и создание базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Административная панель (`shop/admin.py`)

```python
from django.contrib import admin
from .models import Category, Product, ProductImage

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'date_added')
    list_filter = ('category', 'date_added')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
```

---

### 6. URL конфигурация (`catalog_project/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
]
```

---

### 7. Представления (`shop/views.py`)

```python
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
```

---

### 8. Шаблоны

Создайте папки `templates/shop/` и добавьте файлы:

#### `product_list.html`

```html
<!-- templates/shop/product_list.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Каталог товаров</title>
</head>
<body>
    <h1>Каталог товаров</h1>
    <form method="get">
        <input type="text" name="q" placeholder="Поиск..." value="{{ search_query }}">
        <select name="sort">
            <option value="date_added" {% if sort_by == 'date_added' %}selected{% endif %}>По дате добавления</option>
            <option value="name" {% if sort_by == 'name' %}selected{% endif %}>По названию</option>
            <option value="price" {% if sort_by == 'price' %}selected{% endif %}>По цене</option>
        </select>
        <button type="submit">Поиск</button>
    </form>
    <ul>
        {% for product in page_obj.object_list %}
            <li>
                <a href="{{ product.get_absolute_url }}">{{ product.name }}</a><br>
                Цена: {{ product.price }}<br>
                Добавлено: {{ product.date_added }}
            </li>
        {% empty %}
            <li>Нет товаров</li>
        {% endfor %}
    </ul>
    <div>
        {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}&q={{ search_query }}&sort={{ sort_by }}">Пред.</a>
        {% endif %}
        Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}
        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}&q={{ search_query }}&sort={{ sort_by }}">След.</a>
        {% endif %}
    </div>
</body>
</html>
```

#### `product_detail.html`

```html
<!-- templates/shop/product_detail.html -->
<h1>{{ product.name }}</h1>
<p>{{ product.description }}</p>
<p>Цена: {{ product.price }}</p>
<p>Категория: <a href="{{ product.category.get_absolute_url }}">{{ product.category.name }}</a></p>
<p>Дата добавления: {{ product.date_added }}</p>
<h3>Фотографии</h3>
{% for image in product.images.all %}
    <img src="{{ image.image.url }}" width="200" alt="Фото {{ forloop.counter }}">
{% endfor %}
```

#### `category_detail.html`

```html
<!-- templates/shop/category_detail.html -->
<h1>Категория: {{ category.name }}</h1>
{% if category.parent %}
    <p>Родительская категория: <a href="{{ category.parent.get_absolute_url }}">{{ category.parent.name }}</a></p>
{% endif %}
<h2>Подкатегории</h2>
<ul>
    {% for sub in subcategories %}
        <li><a href="{{ sub.get_absolute_url }}">{{ sub.name }}</a></li>
    {% empty %}
        <li>Нет подкатегорий</li>
    {% endfor %}
</ul>
<h2>Товары в категории</h2>
<ul>
    {% for product in products %}
        <li><a href="{{ product.get_absolute_url }}">{{ product.name }}</a></li>
    {% empty %}
        <li>Нет товаров</li>
    {% endfor %}
</ul>
```

---

### 9. Обработка удаления товаров и изображений

Для удаления товаров и их изображений, а также их файлов, можно добавить кастомные действия в админке или реализовать отдельные view с ручным вызовом удаления.

Пример для admin:

```python
# shop/admin.py (добавьте в класс ProductAdmin)

from django.utils.html import mark_safe

class ProductAdmin(admin.ModelAdmin):
    # существующие настройки
    def delete_model(self, request, obj):
        # при удалении товара удаляются и файлы изображений
        for img in obj.images.all():
            img.image.delete(save=False)
        super().delete_model(request, obj)
```

---

### 10. Настройка медиафайлов

Добавьте в `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

И в `urls.py` проекта:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### Запуск проекта

Создание суперпользователя и запуск

Создайте суперпользователя для входа в админку:

python manage.py createsuperuser
Запустите сервер:

python manage.py runserver
Перейдите по адресу http://127.0.0.1:8000/admin/ и войдите под админом. Там вы можете добавлять, редактировать и удалять товары, категории и изображения.

Пользовательская часть доступна по http://127.0.0.1:8000/ 
Админ часть доступна по http://127.0.0.1:8000/admin/

код полность рабочий можете сразу запускать python manage.py runserver админ логин/пароль - admin admin 

снимки экрана примера в папке - _screenshots


### Возможные ошибки

Возможно django захочет работать только с более свежей версией myriadb. Как в ручную обновить mariadb или mysql на свежую версию:

Чтобы обновить MariaDB например в XAMPP в ручную со старой версии до версии 10.5 или новее, необходимо скачать zip-архив MariaDB, распаковать его и заменить существующую папку MySQL в XAMPP распакованными файлами MariaDB. Затем необходимо скопировать папки data, backup и scripts, а также, при необходимости, изменить файл my.ini (но я ничего в my.ini не менял). 

Подробнее:
1. Резервное копирование:
Сначала создайте резервную копию существующей папки mysql в вашей установке XAMPP. Это крайне важно на случай возникновения проблем во время обновления.
2. Скачать MariaDB:
Скачайте соответствующий zip-архив MariaDB с веб-сайта MariaDB https://mariadb.org/download/ Убедитесь, что вы выбрали правильную версию (например, winx64, если у вас 64-битная система).
3. Извлечь MariaDB:
Извлеките загруженный zip-архив в каталог XAMPP. Скорее всего, у вас будет папка с именем, похожим на mariadb-10.5.x-winx64.
4. Переименование и копирование:
Переименуйте исходную папку mysql в каталоге XAMPP (например, в mysql_old).
Переименуйте извлеченную папку MariaDB в mysql.
Переименуйте папку data в mysql_old в data_temp.
Скопируйте папки data, backup и scripts из mysql_old в новую папку mysql.
Скопируйте файлы mysql_uninstallservice.bat и mysql_installservice.bat из mysql_old/bin в mysql/bin.
6. Запустите XAMPP:
Запустите сервер XAMPP.
7. Если не запускается сервер mysql, скорее всего нужно удалить следующие файлы:
mysql/data:
- ib_logfile0
- ib_logfile1
- ibdata1
  
После удаления этих файлов сервер mysql должен запуститься без проблем даже без каких-либо изменений в my.ini
