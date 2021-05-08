from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import logging

logging.basicConfig(level=logging.DEBUG)

# セッションからカートへ遷移する際product識別のためにidをcookieとsessionに登録する


def _cart_id(request):
    cart = request.session.session_key
    # カートセッションに置いてのでバック方法の確認
    request_attribute = dir(request)
    logging.debug('session_key:{}'.format(cart))
    logging.debug('this is request attributes'.format(request_attribute))
    if not cart:
        cart = request.session.create()
        logging.debug('session:{cart}'.format(cart))
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    logging.debug('product:{}'.format(product))

    try:
        # セッションとクッキー内のidを使用してマッチするカートアイテムを取得する
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart
        )
        cart_item.quantite += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantite=1,
        )
        cart_item.save()
    return redirect('cart:cart')


def sub_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantite > 1:
        cart_item.quantite -= 1
        cart_item.save()
    else:
        cart_item.delete()
        return redirect('cart:cart')
    return redirect('cart:cart')
# urlルーティングをする際にurlsで自動的に割り当てられるidとは違い今回はviews側で値の設定を行う


def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart')


def cart(request, total=0, quantite=0, cart_items=None):
    # カート内に必要なデータを抽出
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        logging.debug('cart information:{}'.format(cart))

        for cart_item in cart_items:
            total = + cart_item.product.price * cart_item.quantite
            quantite = + cart_item.quantite
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    return render(request, 'store/cart.html', context={
        'total': total,
        'quantite': quantite,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    })
