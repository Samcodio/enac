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


class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].empty_label = "Select School..."
    class Meta:
        model = Product
        fields = [
            'lodge_name',
            'school',
            'lodge_img',
            'lodge_img2',
            'lodge_img3',
            'lodge_img4',
            'lodge_video',
            'lessor_proof',
            'price',
            'stay_period',
            'description',
            'address',
            'caretaker',
            'light',
            'tiled',
            'upstairs',
            'stable_water',
            'room_number',
            'd_date',
        ]
        widgets = {
            'd_date': DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'room_number': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter Room Name or Number...'
                }
            ),
            'lodge_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your Lodge Name...'
                }
            ),
            'school': Select(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'lodge_img': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',
                }
            ),
            'lodge_img2': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_img3': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_img4': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lessor_proof': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_video': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'video/*',
                }
            ),
            'price': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'required': 'true',
                }
            ),
            'stay_period': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'required': 'true',
                }
            ),
            'address': Textarea(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter the Address...'
                }
            ),
            'description': Textarea(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Leave a notice if needed'
                }
            ),
            'caretaker': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'placeholder': 'Please enter the CareTaker Number...'
                }
            ),
            'tiled': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'stable_water': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'light': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'upstairs': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
        }


class ProductRMForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].empty_label = "Select School..."
    class Meta:
        model = Product
        fields = [
            'lodge_name',
            'school',
            'lodge_img',
            'lodge_img2',
            'lodge_img3',
            'lodge_img4',
            'lodge_video',
            'lessor_proof',
            'price',
            'stay_period',
            'description',
            'address',
            'caretaker',
            'department',
            'level',
            'tiled',
            'upstairs',
            'stable_water',
            'light',
            'room_number',
            'd_date'
        ]
        widgets = {
            'd_date': DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'required': 'true',
                }
            ),
            'room_number': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Please enter Room Name or Number...'
                }
            ),
            'lodge_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your Lodge Name...'
                }
            ),
            'school': Select(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'lodge_img': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',
                }
            ),
            'lodge_img2': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_img3': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_img4': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lessor_proof': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',

                }
            ),
            'lodge_video': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'video/*',
                }
            ),
            'price': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'required': 'true',
                }
            ),
            'stay_period': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'required': 'true',
                }
            ),
            'address': Textarea(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter the Address...'
                }
            ),
            'description': Textarea(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Leave a notice if needed'
                }
            ),
            'caretaker': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'placeholder': 'Please enter the CareTaker Number...'
                }
            ),
            'department': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter your department...'
                }
            ),
            'level': Select(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'tiled': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'stable_water': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'light': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
            'upstairs': CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'type': 'checkbox',
                    'id': 'flexCheckDefault'
                }
            ),
        }


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['school_name', 'school_logo', 'short_version']
        widgets = {
            'school_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter School Name...'
                }
            ),
            'short_version': TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Please enter Abbreviation for School...'
                }
            ),
            'school_logo': FileInput(
                attrs={
                    'type': 'file',
                    'accept': 'image/*',
                    'required': 'true',
                }
            ),
        }

