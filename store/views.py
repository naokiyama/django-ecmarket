from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(
            category=categories, is_available=True).order_by('id')
        product_count = products.count()
        if product_count:
            product_count = 'Number of item:{}'.format(product_count)
        else:
            product_count = 'Not item'
    else:
        # norderedObjectListWarning,productsオブジェクトにidを使用して順序付をする
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 1)
        # requestobjectからpageを取得してpaginatorクラスに渡すとpageオブジェクトが戻り値として返される
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        product_count = products.count()
        if product_count:
            product_count = 'Number of item:{}'.format(product_count)
        else:
            product_count = 'Not item'

    return render(request, 'store/store.html', context={
        'products': page_products,
        'product_count': product_count
    })


def product_detail(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(
            product=single_product, cart__cart_id=_cart_id(request)).exists()

    except Exception as e:
        raise e

    return render(request, 'store/product-detail.html', context={
        'single_product': single_product,
        'in_cart': in_cart
    })
