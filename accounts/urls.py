from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_button, name='logout'),
    path('signUp/', views.signUp, name='signUp'),
    path('change_password/', views.update_password, name='change_password'),
]
