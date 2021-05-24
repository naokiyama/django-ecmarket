from orders.models import OrderProduct
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.urls import NoReverseMatch
from django.db.models import Q
from .forms import ReviewRatingForm
from django.contrib import messages
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# todo
# stockが0以下になった場合の非表示処理とメッサージ表示を行う必要がある
# Create your views here.

logging.basicConfig(level=logging.DEBUG)


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
        paginator = Paginator(products, 2)
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

# reviewをする際に以前商品を購入したことがあるのかをチェックする処理を加える


def product_detail(request, category_slug=None, product_slug=None):

    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(
            product=single_product, cart__cart_id=_cart_id(request)).exists()
        # 逆参照を使ってProductモデルからVariationモデルを取り出す
        variations = single_product.product.all()
        logging.debug('variations:{}'.format(variations.query))

    except Exception as e:
        raise e

    if request.user.is_authenticated:
        # check if user boughts this product
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # get all review
    try:
        review_rating = ReviewRating.objects.filter(
            product_id=single_product.id, status=True)
    except ReviewRating.DoesNotExist:
        review_rating = None

    return render(request, 'store/product-detail.html', context={
        'single_product': single_product,
        'in_cart': in_cart,
        'variations': variations,
        'orderproduct': orderproduct,
        'review_rating': review_rating,
    })


# searchの入力を元にget methodで
def search(request):
    if request.method == 'GET':
        try:
            if 'keyword' in request.GET:
                keyword = request.GET['keyword']
        except NoReverseMatch:
            pass
    else:
        pass

    if keyword:
        # filterメソッドを使い
        logging.debug('keyword:{}'.format(keyword))
        search_product = Product.objects.order_by(
            '-on_created').filter(
                Q(descritpion__icontains=keyword)
                | Q(product_name__icontains=keyword))
        logging.debug('db_query:{}'.format(search_product.query))
        logging.debug('db_query:{}'.format(search_product))
    else:
        search_product = None

    return render(request, 'store/store.html', context={
        'products': search_product,
    })


def submit_review(request, product_id):
    if request.method == 'POST':
        try:
            url = request.META.get('HTTP_REFERER')
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, 'Thank you! Your review has been updated')
            return redirect(url)
        except:

            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                ip = request.META.get('REMOTE_ADDR')
                data = ReviewRating()
                data.product_id = product_id
                data.user_id = request.user.id
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = ip
                data.save()
                messages.success(
                    request, 'Thank you! Your review has been updated')
            return redirect(url)
