from .models import Cart, CartItem
from .views import _cart_id

# カート内商品数をテンプレート全体で使用する定数として取得


def counter(request):
    cart_counter = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            print('counter request:{}'.format(request))
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_counter += cart_item.quantite
        except Cart.DoesNotExist:
            cart_counter = 0
    return dict(cart_counter=cart_counter)
