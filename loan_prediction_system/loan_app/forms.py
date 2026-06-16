from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, LoanApplication, Document

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='applicant'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class OfficerCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Set Password'}),
        validators=[validate_password]
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'officer'  # Force role to officer
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        exclude = ['user', 'prediction', 'ml_prediction', 'prediction_confidence', 'status', 'admin_override', 'admin_notes', 'processed_by', 'processed_at', 'created_at', 'updated_at']
        
        widgets = {
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '18', 'max': '100'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'dependents': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
            'education': forms.Select(attrs={'class': 'form-control'}),
            'self_employed': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'income_annum': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loan_term': forms.NumberInput(attrs={'class': 'form-control', 'min': '6', 'max': '360'}),
            'cibil_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '300', 'max': '900'}),
            'property_area': forms.Select(attrs={'class': 'form-control'}),
            'residential_assets_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commercial_assets_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'luxury_assets_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bank_asset_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class AdminReviewForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add review notes or risk comments...'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file_path']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file_path': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
