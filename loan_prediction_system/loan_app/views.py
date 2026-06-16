from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import UserRegistrationForm, UserLoginForm, LoanApplicationForm, DocumentUploadForm, AdminReviewForm, OfficerCreationForm
from .models import LoanApplication, User
import csv
from datetime import datetime
import sys
import os

# Add ml_model to path to import PredictionEngine
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_model'))
try:
    from predict import PredictionEngine
    predictor = PredictionEngine()
except Exception as e:
    print(f"Failed to load Prediction Engine: {e}")
    predictor = None

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account has been deactivated. Please contact the Admin.')
                    return render(request, 'user/login.html', {'form': form})
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'officer':
                    return redirect('officer_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def user_dashboard_view(request):
    applications = request.user.applications.all().order_by('-created_at')
    context = {
        'total_applications': applications.count(),
        'approved_loans': applications.filter(status='approved').count(),
        'recent_applications': applications[:5],
    }
    return render(request, 'user/dashboard.html', context)

@login_required
def apply_loan_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        doc_form = DocumentUploadForm(request.POST, request.FILES)
        
        if form.is_valid() and doc_form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            
            # Run AI Prediction
            if predictor:
                try:
                    result = predictor.predict(application, use_ann=True)
                    application.ml_prediction = result['status']
                    application.prediction = result['status']
                    application.prediction_confidence = result['confidence']
                except Exception as e:
                    print(f"Prediction failed: {e}")
            
            application.save()
            
            doc = doc_form.save(commit=False)
            doc.application = application
            doc.save()
            
            messages.success(request, 'Loan application submitted successfully!')
            return redirect('prediction_result', application_id=application.id)
    else:
        form = LoanApplicationForm()
        doc_form = DocumentUploadForm()
        
    return render(request, 'user/apply_loan.html', {'form': form, 'doc_form': doc_form})

@login_required
def prediction_result_view(request, application_id):
    application = get_object_or_404(LoanApplication, id=application_id, user=request.user)
    return render(request, 'user/result.html', {'application': application})

@login_required
def emi_calculator_view(request):
    emi_result = None
    form_data = {
        'loan_amount': request.POST.get('loan_amount', ''),
        'interest_rate': request.POST.get('interest_rate', ''),
        'loan_term': request.POST.get('loan_term', ''),
    }

    if request.method == 'POST':
        try:
            loan_amount = float(request.POST.get('loan_amount', 0) or 0)
            interest_rate = float(request.POST.get('interest_rate', 0) or 0)
            loan_term = int(request.POST.get('loan_term', 0) or 0)

            if loan_amount > 0 and loan_term > 0:
                monthly_rate = interest_rate / 100 / 12
                if monthly_rate == 0:
                    emi = loan_amount / loan_term
                else:
                    emi = loan_amount * monthly_rate * (1 + monthly_rate) ** loan_term / ((1 + monthly_rate) ** loan_term - 1)

                total_payment = emi * loan_term
                total_interest = total_payment - loan_amount
                emi_result = {
                    'emi': emi,
                    'total_payment': total_payment,
                    'total_interest': total_interest,
                    'loan_amount': loan_amount,
                    'interest_rate': interest_rate,
                    'loan_term': loan_term,
                }
        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid numeric values for all fields.')
    else:
        # Default professional starting values
        emi_result = {
            'loan_amount': 500000,
            'interest_rate': 10.5,
            'loan_term': 120,
            'emi': 6747,
            'total_payment': 809640,
            'total_interest': 309640,
        }

    return render(request, 'user/emi_calculator.html', {
        'emi_result': emi_result,
        'form_data': form_data,
    })

@login_required
def application_history_view(request):
    applications = request.user.applications.all().order_by('-created_at')
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    prediction_filter = request.GET.get('prediction', '')
    min_amount = request.GET.get('min_amount', '')
    max_amount = request.GET.get('max_amount', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if search_query:
        applications = applications.filter(
            Q(applicant_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    if prediction_filter:
        applications = applications.filter(
            Q(ml_prediction__iexact=prediction_filter) |
            Q(prediction__iexact=prediction_filter)
        )

    try:
        if min_amount:
            applications = applications.filter(loan_amount__gte=float(min_amount))
        if max_amount:
            applications = applications.filter(loan_amount__lte=float(max_amount))
    except ValueError:
        pass

    try:
        if start_date:
            applications = applications.filter(created_at__date__gte=datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            applications = applications.filter(created_at__date__lte=datetime.strptime(end_date, '%Y-%m-%d').date())
    except ValueError:
        pass

    context = {
        'applications': applications,
        'filters': {
            'q': search_query,
            'status': status_filter,
            'prediction': prediction_filter,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    return render(request, 'user/history.html', context)

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user_obj': request.user})

@login_required
def admin_application_list_view(request):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, 'Unauthorized access.')
        return redirect('home')

    applications = LoanApplication.objects.all().order_by('-created_at')
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    prediction_filter = request.GET.get('prediction', '')
    user_query = request.GET.get('user', '')

    if search_query:
        applications = applications.filter(
            Q(applicant_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    if prediction_filter:
        applications = applications.filter(
            Q(ml_prediction__iexact=prediction_filter) |
            Q(prediction__iexact=prediction_filter)
        )

    if user_query:
        applications = applications.filter(user__username__icontains=user_query)

    context = {
        'applications': applications,
        'filters': {
            'q': search_query,
            'status': status_filter,
            'prediction': prediction_filter,
            'user': user_query,
        }
    }
    return render(request, 'admin/applications.html', context)

@login_required
def admin_application_detail_view(request, application_id):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, 'Unauthorized access.')
        return redirect('home')

    application = get_object_or_404(LoanApplication, id=application_id)
    form = AdminReviewForm(request.POST or None, instance=application)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.admin_decision = review.status
        if review.admin_decision in ['approved', 'rejected'] and review.ml_prediction:
            review.admin_override = review.ml_prediction.lower() != review.admin_decision.lower()
            review.prediction_match = review.ml_prediction.lower() == review.admin_decision.lower()
        else:
            review.admin_override = False
            review.prediction_match = False
        from django.utils import timezone
        review.processed_by = request.user
        review.processed_at = timezone.now()
        review.save()
        messages.success(request, 'Application review updated successfully.')
        return redirect('admin_application_detail', application_id=application.id)

    documents = application.documents.all()
    context = {
        'application': application,
        'form': form,
        'documents': documents,
    }
    return render(request, 'admin/application_detail.html', context)

@login_required
def admin_export_applications_csv(request):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, 'Unauthorized access.')
        return redirect('home')

    applications = LoanApplication.objects.all().order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="loan_applications_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Application ID', 'Applicant', 'User', 'Email', 'Phone', 'Loan Amount', 'Loan Term',
        'Income', 'CIBIL Score', 'ML Prediction', 'Prediction Confidence', 'Admin Decision', 'Match', 'Status', 'Submitted At'
    ])

    for app in applications:
        writer.writerow([
            app.id,
            app.applicant_name,
            app.user.username,
            app.email,
            app.phone,
            f'{app.loan_amount:.2f}',
            app.loan_term,
            f'{app.income_annum:.2f}',
            app.cibil_score,
            app.effective_ml_prediction or 'N/A',
            f'{app.prediction_confidence:.2f}' if app.prediction_confidence is not None else 'N/A',
            app.effective_admin_decision or 'N/A',
            'Match' if app.prediction_match else 'Override',
            app.get_status_display(),
            app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response

@login_required
def admin_train_model_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized access.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Import and run training
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_model'))
            from train_model import train_models
            train_models()
            messages.success(request, 'ML models trained successfully!')
        except Exception as e:
            messages.error(request, f'Training failed: {str(e)}')
        return redirect('admin_dashboard')
    
    return render(request, 'admin/train_model.html')

@login_required
def officer_dashboard_view(request):
    if request.user.role != 'officer':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
        
    applications = LoanApplication.objects.all()
    
    # KPIs for Officer (Operational)
    total_apps = applications.count()
    approved_count = applications.filter(status='approved').count()
    rejected_count = applications.filter(status='rejected').count()
    pending_count = applications.filter(status__in=['pending', 'review']).count()
    
    context = {
        'total_applications': total_apps,
        'approved_loans': approved_count,
        'rejected_loans': rejected_count,
        'pending_loans': pending_count,
        'recent_applications': applications.order_by('-created_at')[:10],
    }
    return render(request, 'officer/dashboard.html', context)

@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
        
    import json
    from collections import defaultdict
    from datetime import timedelta
    from django.utils.timezone import now
    
    applications = LoanApplication.objects.all()
    match_count = applications.filter(prediction_match=True).count()
    override_count = applications.filter(prediction_match=False).count()
    
    # KPIs
    total_apps = applications.count()
    global_approved = applications.filter(status='approved').count()
    global_rejected = applications.filter(status='rejected').count()
    global_pending = applications.filter(status__in=['pending', 'review']).count()
    
    approval_rate = round((global_approved / total_apps * 100) if total_apps > 0 else 0)
    total_decisions = match_count + override_count
    match_rate = round((match_count / total_decisions * 100) if total_decisions > 0 else 0)
    
    # Monthly Trends (Last 6 Months)
    from django.utils.timezone import now
    from datetime import timedelta
    from collections import defaultdict
    import json
    
    six_months_ago = now() - timedelta(days=180)
    recent_apps = applications.filter(created_at__gte=six_months_ago)
    
    monthly_data = defaultdict(int)
    for app in recent_apps:
        month_str = app.created_at.strftime('%b %Y')
        monthly_data[month_str] += 1
        
    sorted_months = []
    current = six_months_ago.replace(day=1)
    while current <= now():
        m_str = current.strftime('%b %Y')
        if m_str not in sorted_months:
            sorted_months.append(m_str)
        current += timedelta(days=31)
        current = current.replace(day=1)
        
    month_labels = sorted_months
    month_counts = [monthly_data[m] for m in month_labels]

    # Officer Performance Statistics
    officers = User.objects.filter(role='officer')
    officer_stats = []
    for officer in officers:
        officer_processed = LoanApplication.objects.filter(processed_by=officer)
        off_processed_count = officer_processed.count()
        off_approved_count = officer_processed.filter(status='approved').count()
        officer_stats.append({
            'officer_id': officer.id,
            'username': officer.username,
            'processed_count': off_processed_count,
            'approved_count': off_approved_count,
            'rejected_count': officer_processed.filter(status='rejected').count(),
            'overrides': officer_processed.filter(admin_override=True).count(),
            'approval_rate': round((off_approved_count / off_processed_count * 100) if off_processed_count > 0 else 0)
        })

    context = {
        'total_officers': User.objects.filter(role='officer').count(),
        'total_applicants': User.objects.filter(role='applicant').count(),
        'total_applications': total_apps,
        'approved_loans': global_approved,
        'rejected_loans': global_rejected,
        'pending_loans': global_pending,
        'approval_rate': approval_rate,
        'match_rate': match_rate,
        'matched_decisions': match_count,
        'overridden_decisions': override_count,
        'officer_stats': officer_stats,
        'system_activity': applications.select_related('processed_by').order_by('-created_at')[:10],
        
        # Chart JSON
        'chart_months_json': json.dumps(month_labels),
        'chart_counts_json': json.dumps(month_counts),
        'chart_status_json': json.dumps([global_approved, global_rejected, global_pending]),
        'chart_match_json': json.dumps([match_count, override_count])
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_officer_list_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    
    # Process Creation if it comes from the modal on this page
    if request.method == 'POST' and 'create_officer' in request.POST:
        form = OfficerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Loan Officer successfully registered in the system.")
            return redirect('admin_officer_list')
        else:
            messages.error(request, "Error creating officer. Please check the form data.")
    else:
        form = OfficerCreationForm()

    officers = User.objects.filter(role='officer').order_by('-joined_date')
    officer_data = []
    total_processed = 0
    total_approved = 0
    total_overrides = 0
    
    for officer in officers:
        processed = LoanApplication.objects.filter(processed_by=officer)
        count = processed.count()
        approved = processed.filter(status='approved').count()
        overrides = processed.filter(admin_override=True).count()
        
        total_processed += count
        total_approved += approved
        total_overrides += overrides
        
        officer_data.append({
            'user': officer,
            'processed_count': count,
            'approval_rate': round((approved / count * 100) if count > 0 else 0),
            'override_count': overrides
        })
    
    avg_approval = round((total_approved / total_processed * 100) if total_processed > 0 else 0)
    avg_override = round((total_overrides / total_processed * 100) if total_processed > 0 else 0)

    context = {
        'officers': officer_data,
        'form': form,
        'total_officers': officers.count(),
        'active_officers': officers.filter(is_active=True).count(),
        'disabled_officers': officers.filter(is_active=False).count(),
        'avg_approval_rate': avg_approval,
        'avg_override_rate': avg_override,
    }
    
    return render(request, 'admin/officer_list.html', context)

@login_required
def admin_officer_detail_view(request, officer_id):
    if request.user.role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    
    officer = get_object_or_404(User, id=officer_id, role='officer')
    processed_loans = LoanApplication.objects.filter(processed_by=officer).order_by('-created_at')
    
    context = {
        'officer': officer,
        'processed_loans': processed_loans,
        'total_processed': processed_loans.count(),
        'approved': processed_loans.filter(status='approved').count(),
        'rejected': processed_loans.filter(status='rejected').count(),
        'overrides': processed_loans.filter(admin_override=True).count(),
    }
    return render(request, 'admin/officer_detail.html', context)

@login_required
def admin_toggle_officer_status(request, officer_id):
    if request.user.role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    
    officer = get_object_or_404(User, id=officer_id, role='officer')
    officer.is_active = not officer.is_active
    officer.save()
    
    status = "activated" if officer.is_active else "deactivated"
    messages.success(request, f"Officer {officer.username} has been {status}.")
    return redirect('admin_officer_list')

@login_required
def admin_create_officer_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    
    if request.method == 'POST':
        form = OfficerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Loan Officer account created successfully.")
            return redirect('admin_officer_list')
    else:
        form = OfficerCreationForm()
    
    return render(request, 'admin/create_officer.html', {'form': form})
