from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.student_login, name='login'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('logout/', views.student_logout, name='logout'),
    path('book-room/', views.book_room, name='book_room'),
    path('accommodation/', views.accommodation, name='accommodation'),
    path('hostel-rooms/<str:hostel_type>/', views.hostel_rooms, name='hostel_rooms'),  
    path('payment/<int:booking_id>/', views.make_payment, name='make_payment'),
    path('payment-callback/', views.mpesa_callback, name='mpesa_callback'),
]