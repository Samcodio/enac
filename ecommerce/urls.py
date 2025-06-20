from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'ecommerce'

urlpatterns = [
    path('', views.home, name='home'),
    path('schools/', views.schools, name='schools'),
    path('school&listings/<int:id>/', views.school_lodges, name='school_lodges'),
    path('roommate&listings/<int:id>/', views.school_lodges_roommate, name='school_lodges_roommate'),
    path('lodgeData/<int:id>/', views.lodge_data, name='lodge_data'),
    path('dashboard/', views.profile_dashboard, name='profile_dashboard'),
    path('personal_data/', views.personal_info, name='personal_info'),
    path('edit_data/', views.edit_profile, name='edit_profile'),
    path('edit_lessordata/', views.lessor, name='lessor'),
    path('lessordata/', views.lessor_info, name='lessor_info'),

]