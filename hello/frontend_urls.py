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

    path(
        'create-job/',
        create_job,
        name='create_job'
    ),

    path(
        'company/register/',
        register_company,
        name='register_company'
    ),

    path(
        'company/edit/',
        edit_company,
        name='edit_company'
    ),

    path(
        'profile/edit/',
        edit_profile,
        name='edit_profile'
    ),

    path(
        'jobs/<int:pk>/apply',
        apply_to_job,
        name='apply_to_job'
    ),

    path(
        'dashboard/jobs/<int:job_pk>/applicants/',
        view_applicants,
        name='view_applicants'
    ),

    path(
        'dashboard/applications/<int:app_pk>/status/',
        update_application_status,
        name='update_application_status'),
]
