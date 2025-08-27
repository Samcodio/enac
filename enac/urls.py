"""
URL configuration for enac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import errors
from django.views.generic import TemplateView


handler404 = errors.error_404_view
handler500 = errors.error_500_view
handler403 = errors.error_403_view
handler400 = errors.error_400_view

urlpatterns = [
    path('', include('pwa.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('administer/', admin.site.urls),
    path('', include('ecommerce.urls', namespace='ecommerce')),
    path('auth/', include('django.contrib.auth.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
    path('payment/', include('payment.urls', namespace='payment')),
    path("off/", TemplateView.as_view(template_name="offline.html"), name="offline"),
    path("service-worker.js", TemplateView.as_view(template_name="service-worker.js", content_type="application/javascript"),name="service-worker"),
]
