from django.contrib import admin
from .models import Drug, Inventory, Prescription, PrescriptionItem

# 该文件用于Django管理员后台注册models
# Drug、Inventory、Prescription、PrescriptionItem四个模型已被注册，可以通过admin后台管理界面进行增删改查等操作。


admin.site.register(Drug)
admin.site.register(Inventory)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
