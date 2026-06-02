import os
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, User

# Create your models here.


def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Unsupported file format. Please upload a PDF.')

    # 5MB size limit calculation (5 * 1024 * 1024 bytes)
    if value.size > 5242880:
        raise ValidationError(
            'File size too large. Resumes must be under 5MB.')


class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Company(models.Model):
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='companies'
    )

    def __str__(self):
        return self.company_name


class Job(models.Model):
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100)
    application_link = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    application_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    resume = models.FileField(
        upload_to='resumes/',
        validators=[validate_pdf_extension],
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class PremiumSubscription(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
