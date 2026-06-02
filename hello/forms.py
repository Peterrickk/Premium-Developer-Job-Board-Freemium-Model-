from django import forms
from .models import Job, Company, Role, User, Application


class JobSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search jobs'
        })
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        empty_label="Select your account type...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        # Fields the user needs to fill out manually
        fields = ['company', 'title', 'description',
                  'location', 'salary_range', 'application_link']

        # Adding Bootstrap classes so it looks clean out of the box
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Django Developer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the role, responsibilities, and requirements...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote / New York, NY'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. $90,000 - $120,000'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/apply'}),
        }

    def __init__(self, *args, **kwargs):
        # We pop the user out of the kwargs so parent form initialization doesn't break
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Crucial security check: Filter company options to only show those owned by this user
        if user:
            self.fields['company'].queryset = Company.objects.filter(
                created_by=user)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'location', 'description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. San Francisco, CA'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Briefly describe your company...'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }
