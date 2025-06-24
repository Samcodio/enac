from ecommerce.models import Product, UserProfile
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json


class Wishlist():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # get session key
        wishlist = self.session.get('wishlist_session_key')

        # create session key for new user
        if 'wishlist_session_key' not in request.session:
            wishlist = self.session['wishlist_session_key'] = {}

        # Make session key available everywhere
        self.wishlist = wishlist

    def db_add(self, product, quantity, size=None):
        try:
            product_id = str(product.id)
            if product_id in self.wishlist:
                # If the product is already in the wishlist, update the quantity
                self.wishlist[product_id]['quantity']['quantity'] += quantity
            else:
                # If the product is not in the wishlist, add it with the initial quantity
                self.wishlist.setdefault(product_id, {
                    'quantity': {
                        'price': str(product.price),
                        'quantity': quantity,
                    }
                })
            self.session.modified = True
            if self.request.user.is_authenticated:
                current_user = UserProfile.objects.filter(user__id=self.request.user.id)
                existing_products = Product.objects.filter(id__in=self.wishlist.keys())
                updated_wishlist = {product_id: item for product_id, item in self.wishlist.items() if
                                    int(product_id) in existing_products.values_list('id', flat=True)}
                wishlist_string = json.dumps(updated_wishlist)  # Convert wishlist dictionary to JSON string
                current_user.update(old_cart=wishlist_string)
        except Product.DoesNotExist:
            # If the product does not exist, do not add it to the wishlist
            pass

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.wishlist:
            pass
        else:
            # Store size along with price and quantity
            self.wishlist.setdefault(product_id, {
                'quantity': {
                    'price': str(product.price),
                    'quantity': quantity,
                }
            })
        self.session.modified = True
        if self.request.user.is_authenticated:
            existing_products = Product.objects.filter(id__in=self.wishlist.keys())
            updated_wishlist = {product_id: item for product_id, item in self.wishlist.items() if
                                int(product_id) in existing_products.values_list('id', flat=True)}
            wishlisty = str(updated_wishlist)
            wishlisty = wishlisty.replace("\'", "\"")
            current_user = UserProfile.objects.filter(user__id=self.request.user.id)
            current_user.update(old_cart=str(wishlisty))

    def update(self, product, quantity, size=None):
        product_id = str(product.id)
        if product_id in self.wishlist:
            self.wishlist[product_id]['quantity']['quantity'] = quantity
            self.session.modified = True

    def __len__(self):
        return len(self.wishlist)

    def total_quantities(self):
        total = 0  # Reset total to 0 each time the method is called
        for item in self.wishlist.values():
            if 'quantity' in item:
                if 'quantity' in item['quantity']:
                    total += item['quantity']['quantity']
        return total

    def remove_non_existent_products(self):
        existing_products = Product.objects.filter(id__in=self.wishlist.keys())
        for product_id in list(self.wishlist.keys()):
            if int(product_id) not in existing_products.values_list('id', flat=True):
                del self.wishlist[product_id]
                self.session.modified = True

    def get_prods(self):
        self.remove_non_existent_products()  # Call the correct method
        products = []
        total_sum = Decimal('0.00')
        wishlist_keys = list(self.wishlist.keys())
        for product_id in wishlist_keys:
            try:
                product = Product.objects.filter(sale=True).get(id=int(product_id))
                quantity = int(self.wishlist[product_id]['quantity']['quantity'])
                price = Decimal(self.wishlist[product_id]['quantity']['price'])
                total_price = round(price * quantity, 2)
                product_count = len(wishlist_keys)
                products.append({
                    'id': product.id,
                    'product_obj': product,
                    'product_img': product.lodge_pic,
                    'product_name': product.lodge_name,
                    'quantity': quantity,
                    'price': price,
                    'total_price': total_price,
                })
                total_sum = product_count * 5000
            except Product.DoesNotExist:
                pass
        return products, total_sum

    def get_wishlist_ids(self):
        return list(self.wishlist.keys())

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.wishlist:
            del self.wishlist[product_id]
            self.session.modified = True
            self.total_quantities()
            return True

        return False
