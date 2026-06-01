from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r'jobs', JobViewSet, basename='job')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'users', UserViewSet, basename='user')
router.register(r'subscriptions', PremiumSubscriptionViewSet,
                basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
