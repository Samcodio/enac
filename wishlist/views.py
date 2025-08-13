from django.shortcuts import render, get_object_or_404
from .wishlist import Wishlist
from django.views.decorators.csrf import csrf_exempt
from ecommerce.models import Product
from django.template.loader import render_to_string
from django.http import JsonResponse
import json

# Create your views here.

def wishlist_summary(request):
    wishlist = Wishlist(request)
    wishlist_products, total_sum = wishlist.get_prods()
    context = {
        'wishlist_products': wishlist_products,
        'total_sum': total_sum,
    }
    return render(request, 'Wishlist/wishlist_summary.html', context)


def wishlist_add(request):
    # get the wishlist
    wishlist = Wishlist(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity', 1))

        print(f"Received POST data: product_id={product_id}, quantity={quantity}")

        # look for product in DB
        product = get_object_or_404(Product, id=product_id)
        # save to session
        wishlist.add(product=product, quantity=quantity)

        print(f"Wishlist data after adding: {wishlist.wishlist.get(product_id)}")

        wishlist_quantity = wishlist.total_quantities()
        product_wishlist_data = wishlist.wishlist.get(product_id, {})

        response = JsonResponse({
            'qty': wishlist_quantity,
            'wishlist_data': {
                'product_id': product_id,
                'quantity': quantity,
                'full_wishlist_data': product_wishlist_data
            }
        })
        return response


@csrf_exempt
def wishlist_delete(request):
    if request.POST.get('action') == 'post':
        wishlist = Wishlist(request)
        product_id = request.POST.get('product_id')

        if product_id:
            removed = wishlist.remove(product_id)
            if removed:
                # Get updated wishlist data
                wishlist_products, total_sum = wishlist.get_prods()
                total_quantity = wishlist.total_quantities()

                # # Render the updated wishlist summary HTML
                # wishlist_summary_html = render_to_string('includes/wishlist_summary.html', {
                #     'wishlist_products': wishlist_products,
                #     'total_sum': total_sum
                # }, request=request)

                return JsonResponse({
                    'success': True,
                    'total_quantity': total_quantity,
                    # 'wishlist_summary_html': wishlist_summary_html,
                    'message': 'Item removed from wishlist'
                })

        return JsonResponse({
            'success': False,
            'message': 'Item not found in wishlist'
        }, status=400)

    return JsonResponse({
        'error': 'Invalid request'
    }, status=400)
