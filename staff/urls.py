from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/pharmacist/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('dashboard/finance/', views.finance_dashboard, name='finance_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # 患者专用功能
    path('patient/profile/edit/', views.patient_edit_profile, name='patient_edit_profile'),
    path('patient/visits/', views.patient_visits, name='patient_visits'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('patient/prescriptions/<int:prescription_id>/', views.patient_prescription_detail, name='patient_prescription_detail'),
    path('patient/invoices/', views.patient_invoices, name='patient_invoices'),
    path('patient/invoices/<int:invoice_id>/', views.patient_invoice_detail, name='patient_invoice_detail'),
]

