from django import forms
from ecommerce.models import User
from django.contrib.auth.forms import SetPasswordForm


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Enter your email', max_length=254)



# sign up form
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(
                                   attrs={
                                       'class': 'form-control',
                                       'autofocus': 'true',
                                       'type': 'password',
                                       'required': 'true',
                                       'placeholder': 'Password',
                                       'autocomplete': 'new-password',
                                       'id': 'password1'

                                   }
                               ))
    confirm_password = forms.CharField(label='Confirm Password',
                                       widget=forms.PasswordInput(
                                           attrs={
                                               'class': 'form-control',
                                               'autofocus': 'true',
                                               'type': 'password',
                                               'required': 'true',
                                               'placeholder': 'Confirm Password',
                                               'id': 'password2'
                                           }
                                       ))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': 'true',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Username'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': 'true',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'First Name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': 'true',
                    'type': 'text',
                    'required': 'true',
                    'placeholder': 'Last Name'
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': 'true',
                    'type': 'email',
                    'required': 'true',
                    'placeholder': 'Email'
                }
            )
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password


    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# changing password while logged in
class ChangePasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={
                "class": "form-control",
                "required": "true",
                "placeholder": "Please enter your New Password...",
            }
        )
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={
                "class": "form-control",
                "required": "true",
                "placeholder": "Please Confirm the Password...",
            }
        )
