from django.contrib import admin
from .models import Patient, Visit

# 该文件用于Django管理员后台注册models
# Patient和Visit两个模型已被注册，可以通过admin后台管理界面进行增删改查等操作。


admin.site.register(Patient)
admin.site.register(Visit)
