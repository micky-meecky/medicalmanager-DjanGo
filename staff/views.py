from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import get_user_role, get_user_profile, role_required


def login_view(request):
    """
    登录视图
    支持患者和职工登录
    """
    if request.user.is_authenticated:
        # 如果已登录，重定向到对应的仪表板
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, '请输入用户名和密码。')
            return render(request, 'auth/login.html')
        
        # 使用 Django 的认证系统
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 检查用户是否被禁用
            if not user.is_active:
                messages.error(request, '您的账号已被禁用，请联系管理员。')
                return render(request, 'auth/login.html')
            
            # 登录用户
            login(request, user)
            
            # 检查角色并重定向
            role = get_user_role(user)
            profile = get_user_profile(user)
            
            # 如果是职工，检查是否在职
            if role and role != 'patient' and profile:
                if not profile.is_active:
                    logout(request)
                    messages.error(request, '您的职工账号已被停用，请联系管理员。')
                    return render(request, 'auth/login.html')
            
            messages.success(request, f'欢迎回来，{user.username}！')
            
            # 重定向到仪表板
            return redirect('dashboard')
        else:
            messages.error(request, '用户名或密码错误。')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """登出视图"""
    logout(request)
    messages.success(request, '您已成功登出。')
    return redirect('login')


@login_required
def dashboard(request):
    """
    仪表板视图 - 根据用户角色重定向到对应的仪表板
    """
    role = get_user_role(request.user)
    profile = get_user_profile(request.user)
    
    if role == 'patient':
        return redirect('patient_dashboard')
    elif role == 'doctor':
        return redirect('doctor_dashboard')
    elif role == 'pharmacist':
        return redirect('pharmacist_dashboard')
    elif role == 'finance':
        return redirect('finance_dashboard')
    elif role == 'admin':
        return redirect('admin_dashboard')
    else:
        messages.warning(request, '您的账号未关联任何角色，请联系管理员。')
        return redirect('login')


@login_required
@role_required('patient')
def patient_dashboard(request):
    """患者仪表板"""
    from patients.models import Visit
    from pharmacy.models import Prescription
    from finance.models import Invoice
    
    patient = get_user_profile(request.user)
    visits = Visit.objects.filter(patient=patient).order_by('-visit_time')[:10]
    
    # 统计信息
    total_visits = Visit.objects.filter(patient=patient).count()
    total_prescriptions = Prescription.objects.filter(visit__patient=patient).count()
    total_invoices = Invoice.objects.filter(patient=patient).count()
    unpaid_invoices = Invoice.objects.filter(patient=patient, status='unpaid').count()
    
    context = {
        'patient': patient,
        'recent_visits': visits,
        'total_visits': total_visits,
        'total_prescriptions': total_prescriptions,
        'total_invoices': total_invoices,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'dashboards/patient_dashboard.html', context)


@login_required
@role_required('patient')
def patient_edit_profile(request):
    """患者编辑个人信息"""
    from patients.models import Patient
    from django.contrib import messages
    
    patient = get_user_profile(request.user)
    
    if request.method == 'POST':
        # 更新患者信息
        patient.name = request.POST.get('name', patient.name)
        patient.phone = request.POST.get('phone', patient.phone)
        patient.address = request.POST.get('address', patient.address)
        patient.emergency_contact = request.POST.get('emergency_contact', patient.emergency_contact)
        patient.emergency_phone = request.POST.get('emergency_phone', patient.emergency_phone)
        patient.blood_type = request.POST.get('blood_type', patient.blood_type)
        patient.allergy_history = request.POST.get('allergy_history', patient.allergy_history)
        patient.medical_history = request.POST.get('medical_history', patient.medical_history)
        patient.save()
        
        messages.success(request, '个人信息更新成功！')
        return redirect('patient_dashboard')
    
    context = {
        'patient': patient,
    }
    return render(request, 'patient/edit_profile.html', context)


@login_required
@role_required('patient')
def patient_visits(request):
    """患者查看所有就诊记录"""
    from patients.models import Visit
    
    patient = get_user_profile(request.user)
    visits = Visit.objects.filter(patient=patient).order_by('-visit_time')
    
    context = {
        'patient': patient,
        'visits': visits,
    }
    return render(request, 'patient/visits.html', context)


@login_required
@role_required('patient')
def patient_prescriptions(request):
    """患者查看所有处方"""
    from pharmacy.models import Prescription
    
    patient = get_user_profile(request.user)
    prescriptions = Prescription.objects.filter(
        visit__patient=patient
    ).order_by('-created_at')
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
    }
    return render(request, 'patient/prescriptions.html', context)


@login_required
@role_required('patient')
def patient_prescription_detail(request, prescription_id):
    """患者查看处方详情"""
    from pharmacy.models import Prescription
    from django.shortcuts import get_object_or_404
    from decimal import Decimal
    
    patient = get_user_profile(request.user)
    prescription = get_object_or_404(
        Prescription,
        id=prescription_id,
        visit__patient=patient
    )
    
    items = prescription.items.all()
    total_amount = sum(Decimal(str(item.quantity)) * item.unit_price for item in items)
    
    context = {
        'patient': patient,
        'prescription': prescription,
        'items': items,
        'total_amount': total_amount,
    }
    return render(request, 'patient/prescription_detail.html', context)


@login_required
@role_required('patient')
def patient_invoices(request):
    """患者查看所有账单/发票"""
    from finance.models import Invoice
    
    patient = get_user_profile(request.user)
    invoices = Invoice.objects.filter(patient=patient).order_by('-created_at')
    
    context = {
        'patient': patient,
        'invoices': invoices,
    }
    return render(request, 'patient/invoices.html', context)


@login_required
@role_required('patient')
def patient_invoice_detail(request, invoice_id):
    """患者查看发票详情"""
    from finance.models import Invoice
    from django.shortcuts import get_object_or_404
    
    patient = get_user_profile(request.user)
    invoice = get_object_or_404(
        Invoice,
        id=invoice_id,
        patient=patient
    )
    
    # 获取关联的处方和支付记录
    prescription = None
    if hasattr(invoice.visit, 'prescription'):
        prescription = invoice.visit.prescription
    
    payments = invoice.payments.all().order_by('-paid_at')
    
    context = {
        'patient': patient,
        'invoice': invoice,
        'prescription': prescription,
        'payments': payments,
    }
    return render(request, 'patient/invoice_detail.html', context)


@login_required
@role_required('doctor')
def doctor_dashboard(request):
    """医生仪表板"""
    from patients.models import Visit
    from pharmacy.models import Prescription
    
    staff = get_user_profile(request.user)
    
    # 获取今日就诊
    from django.utils import timezone
    today = timezone.now().date()
    today_visits = Visit.objects.filter(
        doctor=staff,
        visit_time__date=today
    ).order_by('-visit_time')
    
    # 获取待处理处方
    pending_prescriptions = Prescription.objects.filter(
        doctor=staff,
        status='draft'
    ).order_by('-created_at')[:10]
    
    # 获取最近就诊记录
    recent_visits = Visit.objects.filter(
        doctor=staff
    ).order_by('-visit_time')[:10]
    
    context = {
        'staff': staff,
        'today_visits': today_visits,
        'pending_prescriptions': pending_prescriptions,
        'recent_visits': recent_visits,
    }
    return render(request, 'dashboards/doctor_dashboard.html', context)


@login_required
@role_required('pharmacist')
def pharmacist_dashboard(request):
    """药剂师仪表板"""
    from pharmacy.models import Prescription, Inventory, Drug
    from django.db.models import F
    
    staff = get_user_profile(request.user)
    
    # 待发药处方
    pending_prescriptions = Prescription.objects.filter(
        status='issued'
    ).order_by('-created_at')[:10]
    
    # 低库存药品
    low_stock = Inventory.objects.filter(
        quantity__lte=F('warning_level')
    ).select_related('drug')[:10]
    
    # 药品总数
    total_drugs = Drug.objects.filter(is_active=True).count()
    
    context = {
        'staff': staff,
        'pending_prescriptions': pending_prescriptions,
        'low_stock': low_stock,
        'total_drugs': total_drugs,
    }
    return render(request, 'dashboards/pharmacist_dashboard.html', context)


@login_required
@role_required('finance')
def finance_dashboard(request):
    """财务仪表板"""
    from finance.models import Invoice, Payment
    from django.utils import timezone
    from django.db.models import Sum
    
    staff = get_user_profile(request.user)
    
    # 今日待支付发票
    today = timezone.now().date()
    today_unpaid = Invoice.objects.filter(
        status='unpaid',
        created_at__date=today
    ).order_by('-created_at')[:10]
    
    # 今日收入
    today_payments = Payment.objects.filter(
        paid_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # 最近支付记录
    recent_payments = Payment.objects.order_by('-paid_at')[:10]
    
    context = {
        'staff': staff,
        'today_unpaid': today_unpaid,
        'today_payments': today_payments,
        'recent_payments': recent_payments,
    }
    return render(request, 'dashboards/finance_dashboard.html', context)


@login_required
@role_required('admin')
def admin_dashboard(request):
    """管理员仪表板"""
    from patients.models import Patient, Visit
    from pharmacy.models import Drug, Prescription
    from finance.models import Invoice
    from django.db.models import Count
    
    staff = get_user_profile(request.user)
    
    # 统计信息
    stats = {
        'total_patients': Patient.objects.count(),
        'total_visits': Visit.objects.count(),
        'total_drugs': Drug.objects.filter(is_active=True).count(),
        'total_prescriptions': Prescription.objects.count(),
        'total_invoices': Invoice.objects.count(),
    }
    
    # 最近活动
    recent_visits = Visit.objects.order_by('-created_at')[:10]
    
    context = {
        'staff': staff,
        'stats': stats,
        'recent_visits': recent_visits,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)
