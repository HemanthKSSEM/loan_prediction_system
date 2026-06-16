from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('apply-loan/', views.apply_loan_view, name='apply_loan'),
    path('prediction/<int:application_id>/', views.prediction_result_view, name='prediction_result'),
    path('history/', views.application_history_view, name='application_history'),
    path('profile/', views.profile_view, name='profile'),
    path('emi-calculator/', views.emi_calculator_view, name='emi_calculator'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('officer-dashboard/', views.officer_dashboard_view, name='officer_dashboard'),
    path('admin-dashboard/applications/', views.admin_application_list_view, name='admin_application_list'),
    path('admin-dashboard/applications/<int:application_id>/', views.admin_application_detail_view, name='admin_application_detail'),
    path('admin-dashboard/export-csv/', views.admin_export_applications_csv, name='admin_export_applications_csv'),
    path('admin-dashboard/train-model/', views.admin_train_model_view, name='admin_train_model'),
    path('admin-dashboard/officers/', views.admin_officer_list_view, name='admin_officer_list'),
    path('admin-dashboard/officers/create/', views.admin_create_officer_view, name='admin_create_officer'),
    path('admin-dashboard/officers/<int:officer_id>/', views.admin_officer_detail_view, name='admin_officer_detail'),
    path('admin-dashboard/officers/<int:officer_id>/toggle/', views.admin_toggle_officer_status, name='admin_toggle_officer_status'),
]
