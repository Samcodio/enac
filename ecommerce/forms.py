from .models import *
from django.forms import *


# form for editing the user profile
class EditUserInfo(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your username...'
                }
            ),
            'first_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your first name...'
                }
            ),
            'last_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your last name...'
                }
            ),
            'email': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'email',
                    'required': 'true',
                    'placeholder': 'Please enter a valid email...'
                }
            ),
        }


# form for editing the lessor profile
class EditProfileInfo(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_img', 'phone_num', 'phone_num2', 'address', 'full_name']
        widgets = {
            'full_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter your full name...'
                }
            ),
            'phone_num': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter your phone number...'
                }
            ),
            'phone_num2': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter your whatsapp number...'
                }
            ),
            'profile_img': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*'
                }
            ),
            'address': Textarea(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter your address...'
                }
            )
        }
