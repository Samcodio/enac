import json
import requests
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from cart.cart import Cart
from ecommerce.models import Product


def payment_successful(request):
    return render(request, 'Payment/success.html')


def payment_failed(request):
    return render(request, 'Payment/failure.html')


@login_required(login_url='accounts:login')
def payment_initialization(request):
    _, amount = Cart(request).get_prods()
    customer_email = request.user.email
    Initialization = PaymentInitialization(request, customer_email, Decimal(amount))
    return Initialization.initialize_payment()


@login_required(login_url='accounts:login')
def payment_verification(request):
    return PaymentVerifier(request).run()


class PaymentInitialization:
    def __init__(self, request, customer_email, amount):
        self.success_url = None
        self.cancel_url = None
        self.request = request
        self.email = customer_email
        self.amount = int(amount * 100)  # Convert to kobo
        self.api_key = settings.PAYSTACK_SECRET_KEY
        self.back_url = request.META.get('HTTP_REFERER', '/')
        self.session_data = {}
        self.headers = {
            "authorization": f"Bearer {self.api_key}"
        }

    def build_urls(self):
        self.success_url = self.request.build_absolute_uri(
            reverse("payment:verification")
        )
        self.cancel_url = self.back_url

    def prepare_session_data(self):
        metadata = json.dumps({
            "cancel_action": self.cancel_url,
        })
        self.session_data = {
            "email": self.email,
            "amount": self.amount,
            "callback_url": self.success_url,
            "metadata": metadata
        }

    def initialize_payment(self):
        try:
            self.build_urls()
            self.prepare_session_data()

            response = requests.post(
                'https://api.paystack.co/transaction/initialize',
                headers=self.headers,
                data=self.session_data
            ).json()

            if response and response.get("data"):
                return redirect(response["data"]["authorization_url"], code=303)
            else:
                messages.error(self.request, "An error occurred, payment failed. Try again.")
                return redirect('payment:failed')

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError) as e:

            print(f"Error: {e}")
            messages.error(self.request, "A connection error or timeout occurred.")
            return HttpResponseRedirect(self.back_url)


class PaymentVerifier:
    def __init__(self, request):
        self.request = request
        self.cart = Cart(request)
        self.cart_products, self.total_sum = self.cart.get_prods()
        self.reference = request.GET.get('reference')
        self.api_key = settings.PAYSTACK_SECRET_KEY
        self.session_key = 'session_key'
        self.back_url = request.META.get('HTTP_REFERER', '/')

    def has_cart_items(self):
        return bool(self.cart_products)

    def verify_transaction(self):
        url = f"https://api.paystack.co/transaction/verify/{self.reference}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            response = requests.get(url, headers=headers)
            return response.json().get("data", {})
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f'Error: {e}')
            return None

    def handle_successful_transaction(self, transaction_data):
        user = self.request.user
        products_id = [products.get('id', {}) for products in self.cart_products]

        # Add user to products and prevent a single user from been added twice
        products = Product.objects.filter(pk__in=products_id)
        for product in products:
            product.sale = False
            product.save()
            if not product.user.filter(id=user.id).exists():
                product.user.add(user)

        # Remove session data
        if self.session_key in self.request.session:
            del self.request.session[self.session_key]

        print("Transaction successful")
        messages.success(self.request, "Transaction successful")
        return redirect("payment:success")

    def handle_failed_transaction(self):
        print("Transaction not successful")
        messages.error(self.request, "Transaction was not successful. An error occurred.")
        return redirect("payment:failed")

    def run(self):
        if not self.has_cart_items():
            messages.error(self.request, "No item available in cart")
            return redirect("ecommerce:home")

        transaction_data = self.verify_transaction()

        if transaction_data and transaction_data.get("status") == "success":
            return self.handle_successful_transaction(transaction_data)
        elif transaction_data:
            return self.handle_failed_transaction()
        else:
            messages.error(self.request, "A connection error or timeout occurred.")
            return HttpResponseRedirect(self.back_url)


