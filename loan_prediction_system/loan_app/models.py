from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('officer', 'Loan Officer'),
        ('applicant', 'Applicant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='applicant')
    phone = models.CharField(max_length=15, blank=True, null=True)
    employee_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class LoanApplication(models.Model):
    # Personal Details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married')])
    dependents = models.IntegerField(default=0)
    education = models.CharField(max_length=50, choices=[('Graduate', 'Graduate'), ('Not Graduate', 'Not Graduate')])
    
    # Employment Details
    self_employed = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    employment_type = models.CharField(max_length=50, choices=[('Salaried', 'Salaried'), ('Business', 'Business')])
    
    # Financial Details
    income_annum = models.FloatField(default=0.0)
    loan_amount = models.FloatField()
    loan_term = models.IntegerField(help_text="Loan Term in months")
    cibil_score = models.IntegerField(default=300)
    property_area = models.CharField(max_length=20, choices=[('Urban', 'Urban'), ('Semiurban', 'Semiurban'), ('Rural', 'Rural')])
    
    # Assets (Optional / Advanced)
    residential_assets_value = models.FloatField(default=0.0)
    commercial_assets_value = models.FloatField(default=0.0)
    luxury_assets_value = models.FloatField(default=0.0)
    bank_asset_value = models.FloatField(default=0.0)
    
    # System Fields
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('review', 'Under Review'),
    ]
    prediction = models.CharField(max_length=20, blank=True, null=True)
    ml_prediction = models.CharField(max_length=20, blank=True, null=True)
    admin_decision = models.CharField(max_length=20, blank=True, null=True)
    prediction_match = models.BooleanField(default=True)
    prediction_confidence = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_override = models.BooleanField(default=False)
    prediction_match = models.BooleanField(default=False)
    processed_by = models.ForeignKey(User, related_name='processed_loans', null=True, blank=True, on_delete=models.SET_NULL)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"App #{self.id} - {self.applicant_name}"

    @property
    def effective_ml_prediction(self):
        return self.ml_prediction or self.prediction

    @property
    def effective_admin_decision(self):
        if self.admin_decision:
            return self.admin_decision
        if self.status in ['approved', 'rejected', 'review']:
            return self.status
        return None

    @property
    def display_match_status(self):
        if not self.effective_ml_prediction:
            return 'pending'
        return 'match' if self.prediction_match else 'override'

class Document(models.Model):
    DOC_TYPES = [
        ('aadhaar', 'Aadhaar/PAN'),
        ('salary_slip', 'Salary Slip'),
        ('bank_statement', 'Bank Statement'),
        ('photo', 'Applicant Photo'),
        ('other', 'Other Document')
    ]
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    file_path = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for App #{self.application_id}"
