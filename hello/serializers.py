from rest_framework import serializers
from .models import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role_name']


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_name', 'is_premium']
        read_only_fields = ['is_premium']


class CompanySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'location',
                  'description', 'created_by', 'created_by_username']
        read_only_fields = ['created_by']


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source='company.company_name', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'company_name', 'title', 'description',
            'location', 'salary_range', 'application_link', 'created_at', 'is_active'
        ]

    # In serializers.py -> JobSerializer


def to_representation(self, instance):
    representation = super().to_representation(instance)
    request = self.context.get('request')

    # Guard clause: safe checking if user is premium
    is_premium_user = (
        request
        and request.user
        and request.user.is_authenticated
        and getattr(request.user, 'is_premium', False)
    )

    if not is_premium_user:
        representation['salary_range'] = "Only viewable for premium users."
        representation['application_link'] = "Only viewable for premium users."

    return representation


class ApplicationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(
        source='user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'user', 'user_username', 'job',
                  'job_title', 'application_date', 'status']
        read_only_fields = ['user', 'status']


class PremiumSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumSubscription
        fields = ['id', 'user', 'start_date', 'end_date', 'status']
