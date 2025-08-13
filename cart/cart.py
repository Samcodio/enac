from ecommerce.models import Product, UserProfile
from decimal import Decimal
import json


# cart model
class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # get session key
        cart = self.session.get('session_key')

        # create session key for new user
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make session key available everywhere
        self.cart = cart

    # adding items to cart after logging back in
    def db_add(self, product, quantity, size=None):
        try:
            product_id = str(product.id)
            if product_id in self.cart:
                # If the product is already in the cart, update the quantity
                self.cart[product_id]['quantity']['quantity'] += quantity
            else:
                # If the product is not in the cart, add it with the initial quantity
                self.cart.setdefault(product_id, {
                    'quantity': {
                        'price': str(product.price),
                        'quantity': quantity,
                    }
                })
            self.session.modified = True
            if self.request.user.is_authenticated:
                current_user = UserProfile.objects.filter(user__id=self.request.user.id)
                existing_products = Product.objects.filter(id__in=self.cart.keys())
                updated_cart = {product_id: item for product_id, item in self.cart.items() if
                                int(product_id) in existing_products.values_list('id', flat=True)}
                cart_string = json.dumps(updated_cart)  # Convert cart dictionary to JSON string
                current_user.update(old_cart=cart_string)
        except Product.DoesNotExist:
            # If the product does not exist, do not add it to the cart
            pass

    # adding items to cart
    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            pass
        else:
            # Store size along with price and quantity
            self.cart.setdefault(product_id, {
                'quantity': {
                    'price': str(product.price),
                    'quantity': quantity,
                }
            })
        self.session.modified = True
        if self.request.user.is_authenticated:
            existing_products = Product.objects.filter(id__in=self.cart.keys())
            updated_cart = {product_id: item for product_id, item in self.cart.items() if
                            int(product_id) in existing_products.values_list('id', flat=True)}
            carty = str(updated_cart)
            carty = carty.replace("\'", "\"")
            current_user = UserProfile.objects.filter(user__id=self.request.user.id)
            current_user.update(old_cart=str(carty))

    # updating cart(not needed for the project but am not ready to debug this shit if its working fine
    def update(self, product, quantity, size=None):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity']['quantity'] = quantity
            self.session.modified = True

    def __len__(self):
        return len(self.cart)

    # getting quantities in cart
    def total_quantities(self):
        total = 0  # Reset total to 0 each time the method is called
        for item in self.cart.values():
            if 'quantity' in item:
                if 'quantity' in item['quantity']:
                    total += item['quantity']['quantity']
        return total

    # def get_prods(self):
    #     product_ids = self.cart.keys()
    #     products = Product.objects.filter(id__in=product_ids)
    #
    #     return products

    # removing products from cart
    def remove_non_existent_products(self):
        existing_products = Product.objects.filter(id__in=self.cart.keys())
        for product_id in list(self.cart.keys()):
            if int(product_id) not in existing_products.values_list('id', flat=True):
                del self.cart[product_id]
                self.session.modified = True

    # listing products in the cart
    def get_prods(self):
        self.remove_non_existent_products()  # Call the correct method
        products = []
        total_sum = Decimal('0.00')
        cart_keys = list(self.cart.keys())
        for product_id in cart_keys:
            try:
                product = Product.objects.filter(sale=True).get(id=int(product_id))
                quantity = int(self.cart[product_id]['quantity']['quantity'])
                price = Decimal(self.cart[product_id]['quantity']['price'])
                total_price = round(price * quantity, 2)
                product_count = len(cart_keys)
                products.append({
                    'id': product.id,
                    'product_obj': product,
                    'product_img': product.lodge_pic,
                    'product_name': product.lodge_name,
                    'quantity': quantity,
                    'price': price,
                    'total_price': total_price,
                })
                total_sum = product_count * 3000
            except Product.DoesNotExist:
                pass
        return products, total_sum

    def get_cart_ids(self):
        return list(self.cart.keys())

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            self.total_quantities()
            return True
        return False
