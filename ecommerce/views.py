from django.shortcuts import render, get_object_or_404, redirect
from .models import *
import concurrent.futures
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.views import *
from cart.cart import Cart
from wishlist.views import *
from wishlist.wishlist import Wishlist
from cloudinary import uploader
from django.conf import settings
from django.contrib.messages import constants as messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from cloudinary.exceptions import Error as CloudinaryError
from django.contrib import messages
from .forms import *
from cloudinary.uploader import upload as cloudinary_upload
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Create your views here.


# home page, lists out some lodges and schools, basically an intro page
def home(request):
    cheap_list = Product.objects.filter(sale=True, roommate=False).order_by('price')[:10]
    schools = School.objects.all()[:8]
    costly = Product.objects.filter(sale=True, roommate=False).order_by('-price')[:10]
    rm_list = Product.objects.filter(sale=True, roommate=True)[:10]
    context = {
        'cheap_list': cheap_list,
        'schools': schools,
        'costly': costly,
        'rm_list': rm_list
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
@login_required(login_url='accounts:login')
def lodge_data(request, id):
    lodge = get_object_or_404(Product, id=id)
    school = lodge.school
    lodges = Product.objects.filter(sale=True, roommate=False, school=school).exclude(id=id)
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    cart_ids = [int(id) for id in cart.get_cart_ids()]
    # print(cart_ids)
    if request.method == "POST":
        if request.user.norm_user.profile_pic:
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if "request" in request.POST:
                lodge.rm_user.add(request.user)
                # Send email
                subject = 'Recieved Request'
                html_content = render_to_string('Lessor/recieved_request.html', {
                    'user': lodge.lessor,
                })
                text_content = strip_tags(html_content)  # fallback plain-text version

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.EMAIL_HOST_USER,  # From email (use an actual domain or valid email address)
                    [lodge.lessor.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                messages.success(request, 'Added to wishlist')
                return redirect(request.path)
        else:
            messages.warning(request, "Please Complete Your Profile")
    context = {
        'lodge': lodge,
        'lodges': lodges,
        'total_sum': total_sum,
        'cart_ids': cart_ids,
    }
    return render(request, 'User/lodge.html', context)


@login_required(login_url='accounts:login')
# overview dashboard
def profile_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    booked = Product.objects.filter(user=request.user)
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    cart_ids = [int(id) for id in cart.get_cart_ids()]
    carts = len(cart_ids)
    wishlist = Wishlist(request)
    wishlist_ids = [int(id) for id in wishlist.get_wishlist_ids()]
    wishlists = len(wishlist_ids)
    context = {
        'posted_lodges': posted_lodges,
        'booked_count': booked.count(),
        'cart_count': carts,
        'wishlists': wishlists,
        'booked': booked[:10]
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


@login_required(login_url='accounts:login')
# lists out basic information i.e username, first name, last name and email of the logged in user
def personal_info(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges

    }
    return render(request, 'User/personal_info.html', context)


@login_required(login_url='accounts:login')
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


@login_required(login_url='accounts:login')
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


@login_required(login_url='accounts:login')
# lists out the information of the lessor
def lessor_info(request):
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges

    }
    return render(request, 'Lessor/lessor_info.html', context)


@login_required(login_url='accounts:login')
def roommate_requests(request):
    posted_lodges = Product.objects.filter(lessor=request.user, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges
    }
    return render(request, 'Lessor/rrequests.html', context)

@login_required(login_url='accounts:login')
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

                # Send email
                subject = 'Approved Request'
                html_content = render_to_string('Lessor/approved_request.html', {
                    'user': user.username,
                })
                text_content = strip_tags(html_content)  # fallback plain-text version

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.EMAIL_HOST_USER,  # From email (use an actual domain or valid email address)
                    [user.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                messages.success(request, 'Request Approved')
            else:
                pass
        if 'reject' in request.POST:
            user_id = request.POST.get('reject')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                lodge.rm_user.remove(user)
                lodge.save()

                # Send email
                subject = 'Rejected Request'
                html_content = render_to_string('Lessor/reject_request.html', {
                    'user': user.username,
                })
                text_content = strip_tags(html_content)  # fallback plain-text version

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.EMAIL_HOST_USER,  # From email (use an actual domain or valid email address)
                    [user.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                messages.success(request, 'Request Rejected')

            else:
                pass

    context = {
        'lodge': lodge,
        'users': page_obj
    }
    return render(request, 'Lessor/reqList.html', context)


@login_required(login_url='accounts:login')
def bookings(request):
    paid_lodges = Product.objects.filter(user=request.user)
    posted_lodges = Product.objects.filter(lessor=request.user, roommate=True, rm_user__isnull=False).distinct()
    context = {
        'posted_lodges': posted_lodges,
        'paid_lodges': paid_lodges
    }
    return render(request, 'Payment/booked.html', context)


@login_required(login_url='accounts:login')
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


@login_required(login_url='accounts:login')
def create_lodge_product(request):
    if not request.user.norm_user.profile_img:
        messages.error(request, 'Please Complete Your Profile')
        return redirect('ecommerce:lessor_info')
    if not request.user.norm_user.full_name:
        messages.error(request, 'Please Complete Your Profile')
        return redirect('ecommerce:lessor_info')
    cart = Cart(request)
    products, total_sum = cart.get_prods()
    form = ProductForm()

    if request.session.get("uploading_lodge", False):
        messages.warning(request, "An upload is already in progress. Please wait...")
        return redirect('ecommerce:create_lodge_product')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if request.user.norm_user.profile_pic:
            if form.is_valid():
                try:
                    with transaction.atomic():
                        product = form.save(commit=False)
                        product.lessor = request.user

                        # ✅ Collect all images first
                        image_fields = ['lodge_img', 'lodge_img2', 'lodge_img3', 'lodge_img4', 'lessor_proof']
                        image_files = {field: request.FILES.get(field) for field in image_fields if request.FILES.get(field)}

                        # ✅ Validate image sizes before uploading
                        for field, file in image_files.items():
                            if file.size > 5 * 1024 * 1024:
                                messages.warning(request, f'{field} is too large (max 5MB)')
                                return redirect('ecommerce:create_lodge_product')

                        # ✅ Upload images in parallel
                        def upload_image(field, file):
                            return field, cloudinary_upload(
                                file,
                                width=500,
                                height=500,
                                crop='fill',
                                format='jpg'
                            )

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            futures = {executor.submit(upload_image, field, file): field for field, file in image_files.items()}
                            for future in concurrent.futures.as_completed(futures):
                                field, result = future.result()
                                setattr(product, field, result['secure_url'])

                        # ✅ Handle video upload separately
                        if 'lodge_video' in request.FILES:
                            video = request.FILES['lodge_video']
                            if video.size > 50 * 1024 * 1024:
                                messages.warning(request, 'Video file is too large (max 50MB)')
                                return redirect('ecommerce:create_lodge_product')

                            try:
                                result = cloudinary_upload(
                                    video,
                                    resource_type='video',
                                    width=800,
                                    height=600,
                                    crop='fit',
                                    format='mp4'
                                )
                                product.lodge_video = result['secure_url']
                            except CloudinaryError:
                                messages.warning(request, 'Error uploading video')
                                return redirect('ecommerce:create_lodge_product')

                        # ✅ Save product
                        product.save()
                        messages.success(request, 'Listed successfully.')
                        return redirect('ecommerce:lodge_data', id=product.id)

                except Exception as e:
                    messages.error(request, f'An error occurred while listing: {str(e)}')
            else:
                messages.warning(request, 'Form is invalid. Please check your inputs.')
        else:
            messages.error(request, 'Complete Your Profile Please')

    context = {
        'form': form,
        'total_sum': total_sum,
    }
    return render(request, 'Lessor/create_lodge.html', context)


@login_required(login_url='accounts:login')
def create_school(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied')
        return redirect('ecommerce:home')
    form = SchoolForm()

    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    school = form.save(commit=False)

                    school_logo = request.FILES.get('school_logo')
                    if school_logo:
                        if school_logo.size > 5 * 1024 * 1024:  # 5MB limit
                            messages.warning(request, 'School logo is too large (max 5MB)')
                            return redirect('ecommerce:create_school')

                        try:
                            result = cloudinary_upload(
                                school_logo,
                                width=500,
                                height=500,
                                crop='fill',
                                format='jpg'
                            )
                            school.school_logo = result['secure_url']
                        except CloudinaryError:
                            messages.warning(request, 'Error uploading school logo')
                            return redirect('ecommerce:create_school')

                    school.save()
                    messages.success(request, 'School created successfully.')
                    return redirect('ecommerce:home')  # or any success page

            except Exception as e:
                messages.error(request, 'An error occurred while saving school.')

        else:
            messages.warning(request, 'Form is invalid. Please check your inputs.')

    return render(request, 'Admin/create_school.html', {'form': form})


@login_required(login_url='accounts:login')
def create_roommate_product(request):
    if not request.user.norm_user.profile_img:
        messages.error(request, 'Please Complete Your Profile')
        return redirect('ecommerce:lessor_info')
    if not request.user.norm_user.full_name:
        messages.error(request, 'Please Complete Your Profile')
        return redirect('ecommerce:lessor_info')

    cart = Cart(request)
    products, total_sum = cart.get_prods()
    form = ProductRMForm()

    if request.method == 'POST':
        form = ProductRMForm(request.POST, request.FILES)
        if request.user.norm_user.profile_pic:
            if form.is_valid():
                try:
                    with transaction.atomic():
                        product = form.save(commit=False)
                        product.lessor = request.user
                        product.roommate = True

                        # ✅ Collect all images
                        image_fields = ['lodge_img', 'lodge_img2', 'lodge_img3', 'lodge_img4', 'lessor_proof']
                        image_files = {field: request.FILES.get(field) for field in image_fields if request.FILES.get(field)}

                        # ✅ Validate image sizes
                        for field, file in image_files.items():
                            if file.size > 5 * 1024 * 1024:
                                messages.warning(request, f'{field} is too large (max 5MB)')
                                return redirect('ecommerce:create_lodge_product')

                        # ✅ Upload images in parallel
                        def upload_image(field, file):
                            return field, cloudinary_upload(
                                file,
                                width=500,
                                height=500,
                                crop='fill',
                                format='jpg'
                            )

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            futures = {executor.submit(upload_image, field, file): field for field, file in image_files.items()}
                            for future in concurrent.futures.as_completed(futures):
                                field, result = future.result()
                                setattr(product, field, result['secure_url'])

                        # ✅ Handle video upload separately
                        if 'lodge_video' in request.FILES:
                            video = request.FILES['lodge_video']
                            if video.size > 50 * 1024 * 1024:
                                messages.warning(request, 'Video file is too large (max 50MB)')
                                return redirect('ecommerce:create_lodge_product')

                            try:
                                result = cloudinary_upload(
                                    video,
                                    resource_type='video',
                                    width=800,
                                    height=600,
                                    crop='fit',
                                    format='mp4'
                                )
                                product.lodge_video = result['secure_url']
                            except CloudinaryError:
                                messages.warning(request, 'Error uploading video')
                                return redirect('ecommerce:create_lodge_product')

                        # ✅ Save product
                        product.save()
                        messages.success(request, 'Listed successfully.')
                        return redirect('ecommerce:lodge_data', id=product.id)

                except Exception as e:
                    messages.error(request, f'An error occurred while listing: {str(e)}')
            else:
                messages.warning(request, 'Form is invalid. Please check your inputs.')
        else:
            messages.error(request, 'Complete Your Profile Please')

    context = {
        'form': form,
        'total_sum': total_sum,
    }
    return render(request, 'Lessor/create_roommate.html', context)


def faq(request):
    context = {}
    return render(request, 'User/faq.html', context)


def terms(request):
    context = {}
    return render(request, 'User/terms.html', context)


@login_required(login_url='accounts:login')
def admin_checklist(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied')
        return redirect('ecommerce:home')
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'Admin/list.html', context)


@login_required(login_url='accounts:login')
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


def school_roommate(request):
    lodge_list = Product.objects.filter( roommate=True, sale=True)
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
        'lodge_list': page_obj,
        'sort_option': sort_option,
        'school_list': school_list,
    }
    return render(request, 'User/roommates.html', context)


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


@login_required(login_url='accounts:login')
def mylodges(request):
    lodges = Product.objects.filter(lessor=request.user)
    for lodge in lodges:
        lodge.is_sold = lodge.user.exists()
    if request.method == 'POST':
        if 'delete' in request.POST:
            lodge_id = request.POST.get('delete_id')
            product = get_object_or_404(Product, id=lodge_id)
            product.delete()
            messages.success(request, 'Lodge deleted')
            redirect('ecommerce:profile_dashboard')
    context = {
        'lodges': lodges
    }
    return render(request, 'Lessor/mylodges.html', context)


def tutorial(request):
    context = {}
    return render(request, 'User/tutorial.html', context)
