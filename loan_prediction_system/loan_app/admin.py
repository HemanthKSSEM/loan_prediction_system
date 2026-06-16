from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LoanApplication, Document

# Customize the Site Title and Header
admin.site.site_header = "LendSmart AI Control Panel"
admin.site.site_title = "Admin Console"
admin.site.index_title = "System Management Hub"

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Simplify the user management fields
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'loan_amount', 'status', 'created_at')
    list_filter = ('status', 'prediction')
    search_fields = ('applicant_name', 'email')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'uploaded_at')
