from .cart import Cart
from django.conf import settings
from django.contrib.messages import constants as messages


# calling the cart
def cart(request):
    return {'cart': Cart(request)}


# lisitng cart items accross the site
def cart_items(request):
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    max_display_items = getattr(settings, 'CART_MAX_DISPLAY_ITEMS', 2)
    display_items = products[-max_display_items:] if max_display_items else products
    print("Total Sum", total_sum)
    return {'cart_items': products[-2:], 'total_sum': total_sum}


