from .models import Cart, CartItem
from .views import _cart_id

# カート内商品数をテンプレート全体で使用する定数として取得


def counter(request):
    cart_counter = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.all().filter(cart=cart)
        for cart_item in cart_items:
            cart_counter += cart_item.quantite
    except Cart.DoesNotExist:
        cart_counter = 0
    return dict(cart_counter=cart_counter)
