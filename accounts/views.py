from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.messages import constants as messages
from django.contrib import messages
from .forms import *
# from ecommerce.views import BaseView
from ecommerce.models import UserProfile, Product, User
import json
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from cart.cart import Cart
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
# from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages


# from wishlist.wishlist import Wishlist

# Create your views here.


# logging in and re-adding products to cart and wishlist after logging in
def login_page(request):
    if request.user.is_authenticated:
        return redirect("ecommerce:home")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.GET.get('next')  # [New]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            UserProfile.objects.get_or_create(user=user)
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
    if request.user.is_authenticated:
        messages.warning(request, 'Please logout first')
        return redirect("ecommerce:home")
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account successfully created')
            return redirect('accounts:login')
        else:
            # Loop through errors and push them into messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        # Non-field error
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field.capitalize()}: {error}")
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


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No user with that email found.')
                return redirect('accounts:forgot_password')

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = request.build_absolute_uri(
                f'/accounts/reset-password-confirm/{uid}/{token}/'
            )

            # Send email
            subject = 'Password Reset'
            html_content = render_to_string('Authentications/reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            text_content = strip_tags(html_content)  # fallback plain-text version

            email = EmailMultiAlternatives(
                subject,
                text_content,
                'enac-amh7.onrender.com',  # From email (use an actual domain or valid email address)
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            messages.success(request, 'Password reset link sent to your email.')
            return redirect('accounts:forgot_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'Authentications/forgot_password.html', {'form': form})


def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful. You can log in now.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'Authentications/reset_password_confirm.html', {})
    else:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('accounts:forgot_password')

