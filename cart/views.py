from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import logging

logging.basicConfig(level=logging.DEBUG)

# セッションからカートへ遷移する際product識別のためにidをcookieとsessionに登録する

# セッションキーをcartIDとして使用

# セッション、クッキ-がない場合作成


def _cart_id(request):
    cart = request.session.session_key
    request_attribute = dir(request)
    logging.debug('session_key:{}'.format(cart))
    logging.debug('this is request attributes'.format(request_attribute))
    if not cart:
        cart = request.session.create()
    return cart


# カートに商品を追加する
def add_cart(request, product_id):

    product = Product.objects.get(id=product_id)
    # 更新に元の値を保持するためのリスト
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product, variation_choices=key, variation_value=value)
                product_variation.append(variation)
            except ObjectDoesNotExist:
                pass

    try:
        # セッションとクッキー内のidを使用してマッチするカートアイテムを取得する
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    # カートアイテム取得、存在した場合には更新、存在しなかった場合には新規作成
    is_cart_item_exists = CartItem.objects.filter(
        product=product, cart=cart).exists()
    """
    if the cart existing(カートあり): append list
    if the cart not existing: create
    """
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        isexist_list = []  # カート内に追加したプロダクト数
        id = []  # idを識別子として取得
        for item in cart_item:
            exist_variation = item. variations.all()
            isexist_list.append(list(exist_variation))
            id.append(item.id)

        if product_variation in isexist_list:
            # list:isexist_list要素とprodcut_variationにマッチするindexを取得
            index = isexist_list.index(product_variation)
            item_id = id[index]
            cart_item = CartItem.objects.get(product=product, id=item_id)
            cart_item.quantite += 1
            cart_item.save()
        else:
            item = CartItem.objects.create(
                product=product, cart=cart, quantite=1)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)

    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantite=1,
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
            cart_item.save()
    return redirect('cart:cart')


def sub_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    try:
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
        if cart_item.quantite > 1:
            cart_item.quantite -= 1
            cart_item.save()
        else:
            cart_item.delete()
            return redirect('cart:cart')

    except ObjectDoesNotExist:
        pass

    return redirect('cart:cart')
# urlルーティングをする際にurlsで自動的に割り当てられるidとは違い今回はviews側で値の設定を行う


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
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
