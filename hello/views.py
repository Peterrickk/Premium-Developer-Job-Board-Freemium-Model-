# =========================
# FRONTEND VIEWS
# =========================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from rest_framework.viewsets import ModelViewSet

from .forms import RegisterForm
from .models import User, Job, Application, Company, PremiumSubscription

from .serializers import (
    JobSerializer,
    CompanySerializer,
    ApplicationSerializer,
    UserSerializer,
    PremiumSubscriptionSerializer
)

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

    apps = Application.objects.filter(user=request.user)

    print("Applications count:", apps.count())

    for app in apps:
        print(app.user.id, app.user.username, app.job.title)

    return render(request, 'dashboard/dashboard.html', {
        'total_applications': apps.count()
    })

def premium_page(request):
    return render(request, 'subscriptions/premium.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get('website'):
                return redirect('job_list')

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        error = 'Invalid username or password'

    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('job_list')


# =========================
# API VIEWSETS (IMPORTANT FIX)
# =========================

from rest_framework.viewsets import ModelViewSet
from .models import Company, Role, PremiumSubscription


class JobViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PremiumSubscriptionViewSet(ModelViewSet):
    queryset = PremiumSubscription.objects.all()
    serializer_class = PremiumSubscriptionSerializer