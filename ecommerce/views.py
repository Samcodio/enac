from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.views import *
from cart.cart import Cart
from cloudinary import uploader
from django.contrib.messages import constants as messages
from django.db import transaction
from cloudinary.exceptions import Error as CloudinaryError
from django.contrib import messages
from .forms import *
from cloudinary.uploader import upload as cloudinary_upload

from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Create your views here.


# home page, lists out some lodges and schools, basically an intro page
def home(request):
    cheap_list = Product.objects.filter(sale=True, roommate=False).order_by('price')[:10]
    schools = School.objects.all()[:8]
    costly = Product.objects.filter(sale=True, roommate=False).order_by('-price')[:10]
    context = {
        'cheap_list': cheap_list,
        'schools': schools,
        'costly': costly
    }
    return render(request, 'User/index.html', context)


# lists out all schools on the site
def schools(request):
    school_list = School.objects.all()
    paginator = Paginator(school_list, 12)
    page_number = request.GET.get('page')
    page_obj =paginator.get_page(page_number)
    context = {
        "school_list": page_obj
    }
    return render(request, "User/schools.html", context)


# lists out all the lodges belonging to a school
def school_lodges(request, id):
    school = get_object_or_404(School, id=id)
    lodge_list = Product.objects.filter(sale=True, roommate=False, school=school)
    school_list = School.objects.all()
    for sch in school_list:
        sch.lodges = Product.objects.filter(sale=True, roommate=False, school=sch)
        sch.lodges_count = sch.lodges.count()

    # sorting capability
    sort_option = request.GET.get('sort', '')
    if sort_option == 'price_asc':
        lodge_list = lodge_list.order_by('price')
    elif sort_option == 'price_desc':
        lodge_list = lodge_list.order_by('-price')
    elif sort_option == 'newest':
        lodge_list = lodge_list.order_by('-posted_on')
    elif sort_option == 'oldest':
        lodge_list = lodge_list.order_by('posted_on')
    else:
        # Default sorting if none specified
        lodge_list = lodge_list.order_by('-posted_on')

    paginator = Paginator(lodge_list, 12)
    page_number = request.GET.get('page')
    page_obj =paginator.get_page(page_number)
    # print(f"Total items: {len(lodge_list)}")
    # print("Sort option:", sort_option)

    context = {
        'school': school,
        'lodge_list': page_obj,
        'sort_option': sort_option,
        'school_list': school_list,
    }
    return render(request, 'User/schoolLodges.html', context)


# lodge information to be showed
def lodge_data(request, id):
    lodge = get_object_or_404(Product, id=id)
    school = lodge.school
    lodges = Product.objects.filter(sale=True, roommate=False, school=school).exclude(id=id)
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    cart_ids = [int(id) for id in cart.get_cart_ids()]
    # print(cart_ids)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if "request" in request.POST:
            lodge.rm_user.add(request.user)
            messages.success(request, 'Roommate request submitted successfully')
            return redirect(request.path)

    context = {
        'lodge': lodge,
        'lodges': lodges,
        'total_sum': total_sum,
        'cart_ids': cart_ids,
    }
    return render(request, 'User/lodge.html', context)


# overview dashboard
def profile_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges

    }
    return render(request, 'User/profile_dashboard.html', context)


# for lodges in need of roommates in a partiular school
def school_lodges_roommate(request, id):
    school = get_object_or_404(School, id=id)
    lodge_list = Product.objects.filter(school=school, roommate=True, sale=True)
    school_list = School.objects.all()
    for sch in school_list:
        sch.lodges = Product.objects.filter(school=sch, roommate=True, sale=True)
        sch.lodges_count = sch.lodges.count()

    sort_option = request.GET.get('sort', '')
    if sort_option == 'price_asc':
        lodge_list = lodge_list.order_by('price')
    elif sort_option == 'price_desc':
        lodge_list = lodge_list.order_by('-price')
    elif sort_option == 'newest':
        lodge_list = lodge_list.order_by('-posted_on')
    elif sort_option == 'oldest':
        lodge_list = lodge_list.order_by('posted_on')
    else:
        # Default sorting if none specified
        lodge_list = lodge_list.order_by('-posted_on')

    paginator = Paginator(lodge_list, 12)
    page_number = request.GET.get('page')
    page_obj =paginator.get_page(page_number)
    # print(f"Total items: {len(lodge_list)}")
    # print("Sort option:", sort_option)

    context = {
        'school': school,
        'lodge_list': page_obj,
        'sort_option': sort_option,
        'school_list': school_list,
    }
    return render(request, 'User/roommateLodges.html', context)


# lists out basic information i.e username, first name, last name and email of the logged in user
def personal_info(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges

    }
    return render(request, 'User/personal_info.html', context)


# edits the information of the logged in user
def edit_profile(request):
    if request.user.is_authenticated:
        cart = Cart(request)
        products, total_sum = cart.get_prods()
        userform = EditUserInfo(instance=request.user)
        if request.method == 'POST':
            userform = EditUserInfo(request.POST, instance=request.user)
            if userform.is_valid():
                userform.save()
                messages.success(request, 'Changes saved')
                return redirect('ecommerce:personal_info')
            else:
                # print(userform.errors)  # Debugging form errors
                messages.warning(request, 'Invalid details')
        else:
            userform = EditUserInfo(instance=request.user)
        posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
        context = {
            'posted_lodges': posted_lodges,

            'userform': userform,
            'total_sum': total_sum
         }
    else:
        return redirect('accounts:login')
    return render(request, 'User/edit_personal_info.html', context)


# def post_lodges(request):


# edits the lessor profile(the profile of the one that posts the lodge)
def lessor(request):
    if request.user.is_authenticated:
        cart = Cart(request)
        products, total_sum = cart.get_prods()
        profileform = EditProfileInfo(instance=request.user.norm_user)
        if request.method == 'POST':
            profileform = EditProfileInfo(request.POST, request.FILES, instance=request.user.norm_user)
            if profileform.is_valid():
                form = profileform.save(commit=False)
                if 'profile_img' in request.FILES:
                    image_file = request.FILES['profile_img']
                    upload_result = uploader.upload(
                        image_file,
                        width=500,  # Desired width
                        height=500,  # Desired height
                        crop='fill',  # Crop to fill the square
                        format='jpg',  # Output format
                    )
                    # Save the uploaded image URL to the model
                    form.profile_img = upload_result['url']
                else:
                    pass
                form.save()
                messages.success(request, 'Changes saved')
                return redirect('ecommerce:home')
            else:
                # print(profileform.errors)  # Debugging form errors
                messages.warning(request, 'Invalid details')
        else:
            profileform = EditProfileInfo(instance=request.user.norm_user)
        posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
        context = {
            'posted_lodges': posted_lodges,

            'profileform': profileform,
            'total_sum': total_sum
        }
    else:
        return redirect('accounts:login')
    return render(request, 'Lessor/lessor.html', context)


# lists out the information of the lessor
def lessor_info(request):
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges

    }
    return render(request, 'Lessor/lessor_info.html', context)


def roommate_requests(request):
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges
    }
    return render(request, 'Lessor/rrequests.html', context)

def req_list(request, id):
    lodge = get_object_or_404(Product, id=id)
    users = lodge.rm_user.all()
    paginator = Paginator(users, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.method == 'POST':
        if 'approve' in request.POST:
            user_id = request.POST.get('user_id')
            print('user_id', user_id)
            if user_id:
                user = get_object_or_404(User, id=user_id)
                print('User = ', user)
                lodge.approved.add(user)
                lodge.rm_user.remove(user)
                lodge.save()
                messages.success(request, 'Request Approved')
    context = {
        'lodge': lodge,
        'users': page_obj
    }
    return render(request, 'Lessor/reqList.html', context)


def bookings(request):
    paid_lodges = Product.objects.filter(user=request.user)
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges,
        'paid_lodges': paid_lodges
    }
    return render(request, 'Payment/booked.html', context)


def booking_data(request, id):
    lodge = get_object_or_404(Product, id=id)
    school = lodge.school
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    cart_ids = [int(id) for id in cart.get_cart_ids()]
    # print(cart_ids)

    context = {
        'lodge': lodge,
        'total_sum': total_sum,
        'cart_ids': cart_ids,
    }
    return render(request, 'Payment/bookedData.html', context)


def create_lodge_product(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Access denied. You must be logged in.')
        return redirect('ecommerce:home')

    cart = Cart(request)
    products, total_sum = cart.get_prods()
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.lessor = request.user

                    for img_field in ['lodge_img', 'lodge_img2', 'lodge_img3', 'lodge_img4', 'lessor_proof']:
                        file = request.FILES.get(img_field)
                        if file:
                            if file.size > 5 * 1024 * 1024:  # 5MB limit
                                messages.warning(request, f'{img_field} is too large (max 5MB)')
                                return redirect('ecommerce:create_lodge_product')

                            try:
                                result = cloudinary_upload(
                                    file,
                                    width=500,
                                    height=500,
                                    crop='fill',
                                    format='jpg'
                                )
                                setattr(product, img_field, result['secure_url'])
                            except CloudinaryError as e:
                                messages.warning(request, f'Error uploading {img_field}')
                                return redirect('ecommerce:create_lodge_product')

                    # Handle video upload
                    if 'lodge_video' in request.FILES:
                        video = request.FILES['lodge_video']
                        if video.size > 50 * 1024 * 1024:  # 50MB limit
                            messages.warning(request, 'Video file is too large (max 50MB)')
                            return redirect('ecommerce:create_lodge_product')

                        try:
                            result = cloudinary_upload(
                                video,
                                resource_type='video',
                                width=800,
                                height=600,
                                crop='fill',
                                format='mp4'
                            )
                            product.lodge_video = result['secure_url']
                        except CloudinaryError as e:
                            messages.warning(request, 'Error uploading video')
                            return redirect('ecommerce:create_lodge_product')

                    product.save()
                    messages.success(request, 'Lodge Product added successfully.')
                    return redirect('ecommerce:lodge_data', id=product.id)

            except Exception as e:
                messages.error(request, 'An error occurred while saving the product.')
        else:
            messages.warning(request, 'Form is invalid. Please check your inputs.')

    context = {
        'form': form,
        'total_sum': total_sum,
    }
    return render(request, 'Lessor/create_lodge.html', context)


def faq(request):
    context = {}
    return render(request, 'User/faq.html', context)


def terms(request):
    context = {}
    return render(request, 'User/terms.html', context)


def admin_checklist(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied')
        return redirect('ecommerce:home')
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'Admin/list.html', context)

def data(request, id):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied')
        return redirect('ecommerce:home')
    lodge = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            lodge_id = request.POST.get('lodge_id')
            product = get_object_or_404(Product, id=lodge_id)
            product.delete()
            messages.success(request, 'Lodge Terminated')
            return redirect('ecommerce:checklist')
    context = {
        'lodge': lodge
    }
    return render(request, 'Admin/data.html', context)

# cart listing is in the cart app & wishlist in wishlist app
