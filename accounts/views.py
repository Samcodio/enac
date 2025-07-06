from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.messages import constants as messages
from django.contrib import messages
from .forms import *
# from ecommerce.views import BaseView
from ecommerce.models import UserProfile, Product
import json
from cart.cart import Cart


# from wishlist.wishlist import Wishlist

# Create your views here.


# logging in and re-adding products to cart and wishlist after logging in
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.GET.get('next')  # [New]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #  shopping cart stuff
            current_user = UserProfile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            # saved_wishlist = current_user.old_wishlist
            if saved_cart:
                cart_string = saved_cart
                cart_dict = json.loads(cart_string)  # Convert JSON string back to dictionary
                cart = Cart(request)
                cart.remove_non_existent_products()
                for product_id, item in cart_dict.items():
                    try:
                        product = Product.objects.get(id=int(product_id))
                        quantity = item['quantity']['quantity']
                        cart.db_add(product, quantity)
                    except Product.DoesNotExist:
                        pass
            # if saved_wishlist:
            #     wishlist_ string = saved_wishlist
            #     wishlist_dict = json.loads(wishlist_string)  # Convert JSON string back to dictionary
            #     wishlist = Wishlist(request)
            #     wishlist.remove_non_existent_products()
            #     for product_id, item in wishlist_dict.items():
            #         try:
            #             product = Product.objects.get(id=int(product_id))
            #             quantity = item['quantity']['quantity']
            #             wishlist.db_add(product, quantity)
            #         except Product.DoesNotExist:
            #             pass

            # [New]
            if next_url:
                messages.success(request, 'Login Successful')
                return redirect(next_url)

            return redirect('ecommerce:home')
        else:
            messages.warning(request, 'Invalid details')
    context = {}
    return render(request, 'Authentications/login.html', context)


# logout
def logout_button(request):
    logout(request)
    return redirect('accounts:login')


# Signing up
def signUp(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account successfully created')
            return redirect('accounts:login')
        else:
            messages.warning(request, 'Invalid details, re-enter the appropriate characters')
    context = {
        'form': form,
    }
    return render(request, 'Authentications/signup.html', context)


# changing password when logged in
def update_password(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been reset")
                return redirect('accounts:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = ChangePasswordForm(user)
    else:
        return redirect('accounts:login')

    context = {'form': form}
    return render(request, 'Authentications/change_password.html', context)
