from django.db import models
from django.contrib.auth.models import User

"""
    本模块 `staff/models.py` 定义了医院职工的数据模型，适用于医疗管理系统的职工管理功能。

    主要内容如下：

    1. StaffProfile（职工档案）模型
    ----------------------------
    用于扩展 Django 原生的 User 模型，存储职工的业务属性。其属性包括：
    - `user`：关联 Django 原生用户系统（一对一关系），用于登录验证。
    - `staff_no`：工号，唯一，用于业务识别。
    - `name`：职工真实姓名。
    - `role`：岗位角色，决定了该职工在系统中的权限范围（如医生只能开方，财务只能收费）。
    - `department`：所属科室，可选。
    - `position`：职位/职称，可选，如"主任医师"、"副主任医师"、"主治医师"等。
    - `specialty`：专业特长，可选，主要用于医生，描述其专业领域。
    - `phone`：联系电话，可选。
    - `email`：电子邮箱，可选。
    - `address`：联系地址，可选。
    - `hire_date`：入职日期，可选，记录职工入职时间。
    - `is_active`：在职状态，布尔值，控制职工是否在职。
    - `created_at`：创建时间，自动记录数据创建时间。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，便于在 Django 管理后台等处直观显示角色、姓名和工号。

    关系说明
    --------
    - User 与 StaffProfile 为一对一关系（一个系统账号对应一个职工档案）。
    - StaffProfile 与 Visit 为一对多关系（一个医生可以有多个就诊记录）。
    - StaffProfile 与 Prescription 为一对多关系（一个医生可以开具多个处方）。
    - StaffProfile 与 Invoice 为一对多关系（一个财务人员可以开具多张发票）。
    - StaffProfile 与 Payment 为一对多关系（一个财务人员可以处理多笔支付）。

    其他说明
    --------
    - 利用 Django 的 `auth.User` 处理密码哈希和登录 Session，确保安全性。
    - `StaffProfile` 作为 `User` 的"外挂"，存储医疗业务专用的字段。
    - `role` 字段将作为后续开发中"权限控制"的核心依据。
    - 所有文本类字段（如职位、专业特长等）均允许为空并设置了默认值，保证灵活性和数据完整性。
    - 所有模型字段均给出详细注释，方便维护和理解。
    - 添加了适当的唯一约束，提高数据一致性与查询效率。
    - 支持 Django ORM 的相关特性（如 `auto_now_add`、`auto_now`）提升开发便利性。

    此文件结构清晰、设计合理，可方便地扩展使用于职工管理、权限控制等医院管理业务场景。
"""

class StaffProfile(models.Model):
    ROLE_CHOICES = [   # 岗位角色，可选
        ("doctor", "Doctor"),           # 医生：负责就诊、开方
        ("nurse", "Nurse"),             # 护士：负责分诊（预留）
        ("pharmacist", "Pharmacist"),   # 药剂师：负责发药、库存
        ("finance", "Finance"),         # 财务：负责收费
        ("admin", "Admin"),             # 管理员：负责后台维护
    ]

    # 核心关联：一个系统账号对应一个职工档案
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")   # 用户账号，一对一关系
    
    staff_no = models.CharField(max_length=32, unique=True)   # 工号，唯一
    name = models.CharField(max_length=64)   # 真实姓名
    
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="doctor")   # 岗位角色
    department = models.CharField(max_length=64, blank=True, default="General")   # 所属科室
    position = models.CharField(max_length=64, blank=True, default="")   # 职位/职称，可选
    specialty = models.CharField(max_length=128, blank=True, default="")   # 专业特长，可选
    
    phone = models.CharField(max_length=32, blank=True, default="")   # 电话，可选
    email = models.EmailField(blank=True, default="")   # 电子邮箱，可选
    address = models.CharField(max_length=255, blank=True, default="")   # 联系地址，可选
    hire_date = models.DateField(null=True, blank=True)   # 入职日期，可选
    is_active = models.BooleanField(default=True)   # 在职状态，默认为在职
    
    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        # 显示格式：[医生] 张三 (D001)
        return f"[{self.get_role_display()}] {self.name} ({self.staff_no})"