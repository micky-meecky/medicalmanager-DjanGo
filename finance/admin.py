from django.contrib import admin
from .models import Invoice, Payment

# 本文件用于注册 finance 应用的模型到 Django Admin，以便后台管理。
# 请根据实际模型情况（如 Invoice、Payment）在此注册它们，或自定义 Admin 配置。

admin.site.register(Invoice)
admin.site.register(Payment)
