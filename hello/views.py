# =========================
# FRONTEND VIEWS
# =========================

from .models import Company, Role, PremiumSubscription
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .utils import create_audit_log
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser
from django.db.models import Count

from .forms import *
from .models import User, Job, Application, Company, PremiumSubscription

from .serializers import (
    JobSerializer,
    CompanySerializer,
    ApplicationSerializer,
    UserSerializer,
    PremiumSubscriptionSerializer
)


class IsPremiumUserOrReadOnly(BasePermission):
    """
    Allows anyone to view jobs (GET), but only authenticated premium 
    users to create/update them (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in SAFE_METHODS:
            return True

        # Check if user is authenticated and is a premium user
        return request.user and request.user.is_authenticated and request.user.is_premium


class IsEmployerOrReadOnly(BasePermission):
    """
    Allows anyone to view companies (GET), but only users with the 
    'Employer' role to create/modify them.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role and request.user.role.role_name == "Employer"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Ensure the employer modifying the company is the one who created it
        return obj.created_by == request.user


class IsJobSeekerOrEmployerOwner(BasePermission):
    """
    Only authenticated 'Job Seekers' can submit an application (POST).
    Only the Employer who owns the job can modify/view specific application details.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Anyone authenticated can read/list within their object scope
        if request.method in SAFE_METHODS:
            return True

        # Only Job Seekers can create a new application entry
        return request.user.role and request.user.role.role_name == "Job Seeker"

    def has_object_permission(self, request, view, obj):
        # A Job Seeker can view their own application
        if obj.user == request.user:
            return True
        # An Employer can view/edit applications for jobs belonging to their company
        return obj.job.company.created_by == request.user


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('company')

    search = request.GET.get('search', '')
    location = request.GET.get('location', '')

    if search:
        jobs = jobs.filter(title__icontains=search)

    if location:
        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'location': location,
    }

    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    return render(request, 'jobs/job_detail.html', {'job': job})


@login_required
def dashboard(request):
    print("Current user:", request.user.id, request.user.username)

    # Initialize defaults
    company = Company.objects.filter(created_by=request.user).first()
    context = {
        'company': company,
    }

    # Check user role type
    user_role = request.user.role.role_name if request.user.role else "Job Seeker"

    if user_role == "Employer":
        # If they own a registered company, fetch their active job management metrics
        if company:
            # Gather all jobs for this company and attach the total application counts
            company_jobs = Job.objects.filter(company=company).annotate(
                app_count=Count('applications')
            ).order_by('-created_at')
        else:
            company_jobs = Job.objects.none()

        context.update({
            'company_jobs': company_jobs,
            'is_employer': True
        })

    else:
        # Standard Job Seeker metrics
        apps = Application.objects.filter(
            user=request.user).select_related('job__company')
        context.update({
            'total_applications': apps.count(),
            'applications_list': apps,  # Passing down the actual list for future UI features
            'is_employer': False
        })

    return render(request, 'dashboard/dashboard.html', context)


def premium_page(request):
    return render(request, 'subscriptions/premium.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # (Optional honeypot check left intact from your original code)
            if form.cleaned_data.get('website'):
                return redirect('job_list')

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Grab the chosen Role instance
            selected_role = form.cleaned_data['role']

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=selected_role  # Assign the single role here
                )
                messages.success(
                    request, "Account created successfully! Please log in.")
                return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    error = None

    if request.method == 'POST':
        
        if request.POST.get('website'):
            create_audit_log(request, "HONEYPOT TRIGGERED")
            return redirect('job_list')
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            create_audit_log(request, f"LOGIN SUCCESS: {username}")
            return redirect('dashboard')

        create_audit_log(request, f"LOGIN FAILED: {username}")

        error = 'Invalid username or password'

    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('job_list')


@login_required
def create_job(request):
    if not request.user.is_premium:
        messages.error(
            request, "You need a premium subscription to post a job.")
        return redirect('premium')

    if request.method == 'POST':
        # Pass request.POST AND the current user
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        # Pass the current user even on GET requests to filter the initial dropdown
        form = JobForm(user=request.user)

    return render(request, 'jobs/create_job.html', {'form': form})


@login_required
def register_company(request):
    # 1. Enforce Role Restriction: Only Employers allowed
    if not request.user.role or request.user.role.role_name != "Employer":
        messages.error(
            request, "Access denied. Only Employer accounts can register a company.")
        return redirect('dashboard')

    # 2. Block non-premium users
    if not request.user.is_premium:
        messages.error(
            request, "You need a premium subscription to register a company.")
        return redirect('dashboard')

    # 3. Block if they already own a company
    existing_company = Company.objects.filter(created_by=request.user).exists()
    if existing_company:
        messages.warning(request, "You have already registered a company.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, "Company registered successfully!")
            return redirect('dashboard')
    else:
        form = CompanyForm()

    return render(request, 'companies/register_company.html', {'form': form})


@login_required
def edit_company(request):
    # 1. Enforce Role Restriction: Only Employers allowed
    if not request.user.role or request.user.role.role_name != "Employer":
        messages.error(
            request, "Access denied. Only Employer accounts can modify company details.")
        return redirect('dashboard')

    # 2. Ensure the employer is still a premium member
    if not request.user.is_premium:
        messages.error(
            request, "You need an active premium subscription to manage a company.")
        return redirect('dashboard')

    # 3. Fetch the company instance belonging to this user
    company = get_object_or_404(Company, created_by=request.user)

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated successfully!")
            return redirect('dashboard')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/edit_company.html', {'form': form, 'company': company})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your profile details have been updated!")
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def apply_to_job(request, pk):
    if request.user.role and request.user.role.role_name == "Employer":
        messages.error(request, "Employers cannot apply to job postings.")
        return redirect('job_list')

    if not request.user.is_premium:
        messages.error(
            request, "You need a premium subscription to apply for this job.")
        return redirect('premium')

    job = get_object_or_404(Job, pk=pk)

    # Double application block guard
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.warning(
            request, "You have already submitted an application record for this job.")
        return redirect('job_list')

    if request.method == 'POST':
        # CRITICAL: We pass request.FILES alongside request.POST to grab file buffers!
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.status = 'Pending'
            application.save()  # Saves file to /media/resumes/ locally!

            messages.success(
                request, f"Resume tracked! Redirecting you to {job.company.company_name}...")

            target_url = job.application_link
            if not target_url.startswith(('http://', 'https://')):
                target_url = f'https://{target_url}'
            return redirect(target_url)
    else:
        form = JobApplicationForm()

    return render(request, 'jobs/submit_application.html', {'form': form, 'job': job})


@login_required
def view_applicants(request, job_pk):
    # Security: Ensure only Employers can look at candidate records
    if not request.user.role or request.user.role.role_name != "Employer":
        messages.error(
            request, "Access denied. Only Employers can view applicant pools.")
        return redirect('dashboard')

    # Fetch the job and verify it belongs to the logged-in employer's company
    job = get_object_or_404(Job, pk=job_pk, company__created_by=request.user)

    # Grab all candidate applications for this specific job posting
    applicants = job.applications.select_related(
        'user').order_by('-application_date')

    return render(request, 'dashboard/view_applicants.html', {
        'job': job,
        'applicants': applicants,
        'status_choices': ['Pending', 'Reviewed', 'Accepted', 'Rejected']
    })


@login_required
def update_application_status(request, app_pk):
    if not request.user.role or request.user.role.role_name != "Employer":
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    # Security check: Ensure the application belongs to a job posted by THIS employer
    application = get_object_or_404(
        Application, pk=app_pk, job__company__created_by=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Reviewed', 'Accepted', 'Rejected']:
            application.status = new_status
            application.save()
            messages.success(
                request, f"Updated {application.user.username}'s application status to {new_status}.")
        else:
            messages.error(request, "Invalid status assignment choice.")

    return redirect('view_applicants', job_pk=application.job.pk)

# =========================
# API VIEWSETS (IMPORTANT FIX)
# =========================


class JobViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsPremiumUserOrReadOnly]


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsEmployerOrReadOnly]


class ApplicationViewSet(ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsJobSeekerOrEmployerOwner]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Application.objects.none()

        # If they are an employer, show apps for jobs belonging to their company
        if getattr(user.role, 'role_name', None) == "Employer":
            return Application.objects.filter(job__company__created_by=user)

        # If they are a job seeker, only show their own applications
        return Application.objects.filter(user=user)

    def perform_create(self, serializer):
        # Automatically bind the authenticated API user to their application asset
        serializer.save(user=self.request.user, status='Pending')


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class PremiumSubscriptionViewSet(ModelViewSet):
    queryset = PremiumSubscription.objects.all()
    serializer_class = PremiumSubscriptionSerializer
    permission_classes = [IsAdminUser]
