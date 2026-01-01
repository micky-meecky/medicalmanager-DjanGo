from django.shortcuts import get_object_or_404, render
from .models import Patient, Visit


def patient_list(request):
    # 1. 去数据库拿所有病人
    patients = Patient.objects.all().order_by('-created_at')
    # 2. 把数据打包发给 HTML
    return render(request, 'patient_list.html', {'patients': patients})


def patient_detail(request, id):
    # 去 Patient 表里找 id 等于传入 id 的那个人
    # 如果找不到，Django 会自动报错 404
    patient = get_object_or_404(Patient, id=id)
    
    # 把找到的 patient 打包发给页面
    return render(request, 'patient_detail.html', {'patient': patient})