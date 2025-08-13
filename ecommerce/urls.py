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
    path('roommateOptions/', views.roommate_requests, name='roommate_requests'),
    path('recivedRequests/<int:id>/', views.req_list, name='req_list'),
    path('bookings/', views.bookings, name='bookings'),
    path('BookingData/<int:id>/', views.booking_data, name='booking_data'),
    path('list-lodge/', views.create_lodge_product, name='create_lodge_product'),
    path('list-rm/', views.create_roommate_product, name='create_roommate_product'),
    path('faq/', views.faq, name='faq'),
    path('terms_&_conditions/', views.terms, name="terms"),
    path('list/', views.admin_checklist, name='checklist'),
    path('info/<int:id>/', views.data, name='data'),
    path('roommatelistings/', views.school_roommate, name='roommates'),
    path('add-school/', views.create_school, name='create_school'),
    path('my-posts/', views.mylodges, name='my_lodges'),
    path('help/', views.tutorial, name='tutorial')
]