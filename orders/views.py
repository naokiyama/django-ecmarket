from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.http import JsonResponse

from django.core.exceptions import ObjectDoesNotExist

import json
import datetime

# email
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# todo
# Product stock 在庫数の照合をする必要がある
# Create your views here.


def place_order(request):
    current_user = request.user
    cart_item = CartItem.objects.filter(user=current_user)
    item_count = len(cart_item)
    if item_count <= 0:
        return redirect('store:store')

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0
    for item in cart_item:
        total += item.product.price * item.quantite
        quantity += item.quantite
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        print('post')
        if order_form.is_valid():
            print('is valid success')
            data = Order()
            data.user = current_user
            data.first_name = order_form.cleaned_data['first_name']
            data.last_name = order_form.cleaned_data['last_name']
            data.phone_number = order_form.cleaned_data['phone_number']
            data.email = order_form.cleaned_data['email']
            data.adress_line = order_form.cleaned_data['adress_line']
            data.city = order_form.cleaned_data['city']
            data.state = order_form.cleaned_data['state']
            data.country = order_form.cleaned_data['country']
            data.postal_code = order_form.cleaned_data['postal_code']
            data.order_note = order_form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))

            d = datetime.date(year, month, day)
            current_date = d.strftime("%Y%m%d")
            # 日付+プライマリキーidを注文番号にする
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_orderd=False, order_number=order_number)
            return render(request, 'orders/payment.html', context={
                'order': order,
                'cart_items': cart_item,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,

            })

        else:
            print('failed')
            return redirect('cart:checkout')


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_orderd=False, order_number=body['orderID'])
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()
    order.payment = payment
    order.is_orderd = True
    order.save()

    # move the cart item to order product item

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product.id
        order_product.quantity = item.quantite
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variations = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variations)
        order_product.save()

        # reduce quantity of the product
        product = Product.objects.get(id=item.product.id)
        product.stock -= order_product.quantity
        product.save()

    # clear item in the user cart
    CartItem.objects.filter(user=request.user).delete()

    # send a email to customer for confirm order
    user = request.user
    order = Order.objects.get(
        user=user, is_orderd=True, order_number=body['orderID'])
    email = order.email
    subject = 'Your order is complete'
    message = render_to_string('orders/order_verification_mail.html', {
        'user': user,
        'order': order
    })
    to_email = email
    send_email = EmailMessage(subject, message, to=[to_email])
    send_email.send()

    # send order number and transanction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    # store trasaction details inside payment model
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_orderd=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        sub_total = order.order_total - order.tax
        payment = Payment.objects.get(payment_id=transID)

        return render(request, "orders/order_complete.html", context={
            'order': order,
            'order_products': order_products,
            'order_number': order_number,
            'transaction': payment.payment_id,
            'payment': payment,
            'sub_total': sub_total,
        })
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
