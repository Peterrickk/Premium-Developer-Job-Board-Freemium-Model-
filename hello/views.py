from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from .serializers import *

# Create your views here.


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'created_by') and obj.created_by is not None:
            return obj.created_by == request.user

        if hasattr(obj, 'company') and obj.company is not None:
            return obj.company.created_by == request.user

        if hasattr(obj, 'user') and obj.user is not None:
            return obj.user == request.user

        return False


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related('company')

    def perform_create(self, serializer):
        company = serializer.validated_data['company']
        if company.created_by != self.request.user:
            raise PermissionDenied(
                "The company owner can only make these changes.")
        serializer.save()


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().select_related('created_by')
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        return Application.objects.filter(
            Q(user=user) | Q(job__company__created_by=user)
        ).distinct().select_related('user', 'job__company')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PremiumSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = PremiumSubscription.objects.all()
    serializer_class = PremiumSubscriptionSerializer
    permission_classes = [IsAuthenticated]
