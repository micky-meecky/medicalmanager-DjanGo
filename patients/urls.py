from django.urls import path
from . import views

# urls.py 的作用就是：把 URL 和视图函数关联起来，这样当用户访问某个 URL 时，Django 就会调用对应的视图函数来处理请求。说得通俗点，就是告诉 Django，当用户访问 /patients/ 时，应该调用 views.py 中的 patient_list 函数来处理；当用户访问 /patients/1/ 时，应该调用 views.py 中的 patient_detail 函数来处理。

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('<int:id>/', views.patient_detail, name='patient_detail'),
]