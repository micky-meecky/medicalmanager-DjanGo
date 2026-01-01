"""
认证和权限装饰器模块
用于实现基于角色的访问控制
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def role_required(*allowed_roles):
    """
    基于角色的访问控制装饰器
    
    用法：
    @role_required('doctor', 'admin')
    def my_view(request):
        ...
    
    参数：
    - allowed_roles: 允许访问的角色列表，如 'doctor', 'pharmacist', 'finance', 'admin', 'patient'
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            user = request.user
            
            # 检查是否是患者
            if 'patient' in allowed_roles:
                if hasattr(user, 'patient_profile'):
                    return view_func(request, *args, **kwargs)
            
            # 检查是否是职工
            if hasattr(user, 'staff_profile'):
                staff = user.staff_profile
                if not staff.is_active:
                    messages.error(request, '您的账号已被停用，请联系管理员。')
                    return redirect('login')
                
                if staff.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            # 没有权限
            messages.error(request, '您没有权限访问此页面。')
            return redirect('dashboard')
        
        return wrapped_view
    return decorator


def get_user_role(user):
    """
    获取用户的角色
    
    返回：
    - 'patient': 患者
    - 'doctor': 医生
    - 'pharmacist': 药剂师
    - 'finance': 财务
    - 'admin': 管理员
    - 'nurse': 护士
    - None: 未登录或未关联角色
    """
    if not user.is_authenticated:
        return None
    
    # 检查是否是患者
    if hasattr(user, 'patient_profile'):
        return 'patient'
    
    # 检查是否是职工
    if hasattr(user, 'staff_profile'):
        return user.staff_profile.role
    
    return None


def get_user_profile(user):
    """
    获取用户的业务档案（Patient 或 StaffProfile）
    
    返回：
    - Patient 对象（如果是患者）
    - StaffProfile 对象（如果是职工）
    - None（如果未关联）
    """
    if not user.is_authenticated:
        return None
    
    if hasattr(user, 'patient_profile'):
        return user.patient_profile
    
    if hasattr(user, 'staff_profile'):
        return user.staff_profile
    
    return None

