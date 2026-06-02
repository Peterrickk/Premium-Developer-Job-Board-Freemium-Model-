from django.urls import path
from .views import *

urlpatterns = [

    path('', job_list, name='job_list'),

    path(
        'jobs/<int:pk>/',
        job_detail,
        name='job_detail'
    ),

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    path(
        'premium/',
        premium_page,
        name='premium'
    ),

    path(
        'register/',
        register_view,
        name='register'
    ),

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),
]