

from django.urls import path
from . import views

urlpatterns = [
    #user registration and login
    path('register/',views.registerUser,name='register'),
    path('login/', views.loginUser,name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('',views.home, name='home'),
    path('user/', views.userPage, name='userpage'),

    path('account/', views.accountSettings, name='account'),
    # path('useraccount/', views.accountSettings, name='useraccount'),


    path('products/',views.products, name='products'),
    path('customer/<str:pk>/',views.customer, name='customer'),

    #crud urls

    path('create_order/<str:pk>/',views.createOrder,name='create_order'),
    path('update_order/<str:pk>/',views.updateOrder, name='update_order'),
    path('delete_order/<str:pk>/', views.deleteOrder, name='delete_order'),
]