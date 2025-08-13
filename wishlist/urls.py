from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_summary, name="wishlist_summary"),
    path('add/', views.wishlist_add, name="wishlist_add"),
    path('wishlist-del/', views.wishlist_delete, name="wishlist_delete"),
    # path('wishlist-upd/', views.update_wishlist, name="update_wishlist"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
