from .wishlist import Wishlist
from django.conf import settings
from django.contrib.messages import constants as messages


def wishlist(request):
    return {'wishlist': Wishlist(request)}


def wishlist_items(request):
    wishlist = Wishlist(request)
    products, total_sum = wishlist.get_prods()
    print("Total Sum", total_sum)
    return {'wishlist_items': products[-2:], 'total_sum': total_sum}


