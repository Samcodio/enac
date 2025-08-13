from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('initialization/', views.payment_initialization, name="initialization"),
    path('verification/', views.payment_verification, name="verification"),
    path('successful/', views.payment_successful, name="success"),
    path('failed/', views.payment_failed, name="failed"),
]
