from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary import CloudinaryImage
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload
from cloudinary.models import CloudinaryField
from PIL import Image
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)


# User profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='norm_user')
    full_name = models.CharField(max_length=255, null=True, blank=True)
    profile_img = CloudinaryField('image', null=True, blank=True)
    phone_num = models.CharField(max_length=12, null=True, blank=True)
    phone_num2 = models.CharField(max_length=12, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    # for adding to cart after logging out and logging back in
    old_cart = models.CharField(max_length=1000, null=True, blank=True)
    # for adding to wishlist after logging out and logging back in
    old_wishlist = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    mute = models.BooleanField(default=False)

    @property
    def profile_pic(self):
        if self.profile_img:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.profile_img)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None


# school model
class School(models.Model):
    school_name = models.CharField(max_length=255)
    school_logo = CloudinaryField('image', null=True, blank=True)
    short_version = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['school_name']

    @property
    def logo_pic(self):
        if self.school_logo:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.school_logo)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None

    def __str__(self):
        return self.school_name

    def get_absolute_url(self):
        return reverse('ecommerce:school_detail', args=[self.id])


# Lodges (named as Product models)
class Product(models.Model):
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
        ('600', '600 Level'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school')
    # users that have paid for the contact of the lodge
    user = models.ManyToManyField(User, blank=True, related_name='paidUsers')
    rm_user = models.ManyToManyField(User, blank=True, related_name='requesters')
    address = models.CharField(max_length=255, null=True, blank=True)
    caretaker = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    room_number = models.CharField(max_length=255, null=True, blank=True)
    d_date = models.DateField(null=True, blank=True)
    level = models.CharField(max_length=255, null=True, blank=True, choices=LEVEL_CHOICES)
    # the user that posted the lodge
    lessor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_products', null=True, blank=True)
    lodge_name = models.CharField(max_length=100)
    lodge_img = CloudinaryField('image', null=True, blank=True)
    lodge_img2 = CloudinaryField('image', null=True, blank=True)
    lodge_img3 = CloudinaryField('image', null=True, blank=True)
    lodge_img4 = CloudinaryField('image', null=True, blank=True)
    lodge_video = CloudinaryField(resource_type="video", null=True, blank=True,
                                   help_text="Upload a video file")
    # image of the person that posted the lodge
    lessor_proof = CloudinaryField('image', null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stay_period = models.IntegerField(default=12)
    description = models.TextField(null=True, blank=True, default='')
    posted_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # on sale?
    sale = models.BooleanField(default=True)
    # roommate needed?
    roommate = models.BooleanField(default=False)
    tiled = models.BooleanField(default=False)
    upstairs = models.BooleanField(default=False)
    stable_water = models.BooleanField(default=False)
    light = models.BooleanField(default=False)
    approved = models.ManyToManyField(User, blank=True, related_name='approvedusers')
    def get_absolute_url(self):
        """this is used to get the detail url for order"""
        return reverse('ecommerce:product_detail',
                       args=[self.pk])

    @property
    def lodge_pic(self):
        if self.lodge_img:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.lodge_img)).build_url(
                width=500,
                height=500,
                crop='fill',
                format='jpg'
            )
        return None

    @property
    def lodge_pic2(self):
        if self.lodge_img2:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.lodge_img2)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None

    @property
    def lodge_pic3(self):
        if self.lodge_img3:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.lodge_img3)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None

    @property
    def lodge_pic4(self):
        if self.lodge_img4:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.lodge_img4)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None

    @property
    def lessor_pic(self):
        if self.lessor_proof:
            # Use Cloudinary's image transformation to resize the image
            return CloudinaryImage(str(self.lessor_proof)).build_url(width=500, height=500, crop='fill', format='jpg')
        else:
            return None

    @property
    def lodge_vid(self):
        if self.lodge_video:
            # Generate Cloudinary URL for the video with optional transformations
            url, options = cloudinary_url(
                self.lodge_video.public_id,
                resource_type="video",
                format="mp4",
                width=800, height=600, crop="fill"
            )
            return url
        return None

    def __str__(self):
        return self.lodge_name


class ReqList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile whenever a new User is created.
    Also ensures existing users have a profile.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        # For existing users, ensure they have a profile
        if not hasattr(instance, 'norm_user'):
            UserProfile.objects.get_or_create(user=instance)  # This ensures the profile exists even if signal failed earlier


@receiver(post_save, sender=Product)
def create_token(sender, instance, created, **kwargs):
    if created and instance.lessor:
        ReqList.objects.create(user=instance.lessor, product=instance)
        instance.save()