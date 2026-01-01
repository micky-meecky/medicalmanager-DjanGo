from django.db import models


"""
    本模块 `patients/models.py` 定义了与患者基本信息和就诊记录相关的数据模型，适用于医疗管理系统的数据存储与管理。

    主要内容如下：

    1. Patient（患者）模型
    --------------------
    用于存储患者的基本个人信息。其属性包括：
    - `patient_no`：患者编号，唯一，用于区分不同患者。
    - `name`：患者姓名。
    - `gender`：性别，有三个选项（男、女、其他）。
    - `date_of_birth`：出生日期，可选，允许留空。
    - `phone`：联系电话，可选，可为空字符串，并创建索引以便高效检索。
    - `id_number`：身份证号，唯一，可选。
    - `address`：住址/联系地址，可选。
    - `emergency_contact`：紧急联系人姓名，可选。
    - `emergency_phone`：紧急联系人电话，可选。
    - `blood_type`：血型，可选，如 A、B、AB、O 等。
    - `allergy_history`：过敏史，文本字段，可选。
    - `medical_history`：既往病史，文本字段，可选。
    - `created_at`：创建时间，自动记录数据创建时间。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，便于在 Django 管理后台等处直观显示患者编号和姓名。

    2. Visit（就诊记录）模型
    ----------------------
    记录每次患者的就诊信息。其属性包括：
    - `visit_no`：就诊编号，唯一。
    - `patient`：关联的患者（外键，级联保护），一个患者可以关联多个就诊记录。
    - `doctor`：关联的医生（外键，保护删除），可选，记录负责本次就诊的医生。
    - `department`：就诊科室，可选。
    - `visit_time`：就诊时间。
    - `chief_complaint`：主诉，描述患者本次就诊的主要诉求，可选。
    - `diagnosis`：诊断信息，可选。
    - `notes`：备注信息，可选。
    - `status`：就诊状态，包括开放（open）、关闭（closed）、取消（cancelled），可由用户选择，默认为"开放"。
    - `next_visit_date`：建议复诊日期，可选。
    - `created_at`：创建时间，自动记录。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型也实现了 `__str__` 方法，返回就诊编号和关联患者姓名，便于识别。

    关系说明
    --------
    - 一个 Patient 可以有多个 Visit（患者与就诊记录为一对多关系）。
    - 每条 Visit 通过外键 `patient` 明确关联到对应的 Patient。
    - 一个 StaffProfile（医生）可以有多个 Visit（医生与就诊记录为一对多关系）。
    - 每条 Visit 通过外键 `doctor` 可选关联到对应的 StaffProfile（医生）。

    其他说明
    --------
    - 所有文本类字段（如备注、主诉等）均允许为空并设置了默认值，保证灵活性和数据完整性。
    - 所有模型字段均给出详细注释，方便维护和理解。
    - 添加了适当的唯一约束和索引，提高数据一致性与查询效率。
    - 支持 Django ORM 的相关特性（如 `auto_now_add`）提升开发便利性。

    此文件结构清晰、设计合理，可方便地扩展使用于门诊、住院等多场景医疗信息管理系统。
"""




class Patient(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    patient_no = models.CharField(max_length=32, unique=True)   # 患者编号，唯一
    name = models.CharField(max_length=64)   # 姓名
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)   # 性别，可选
    date_of_birth = models.DateField(null=True, blank=True)   # 出生日期，可选

    phone = models.CharField(max_length=32, db_index=True, blank=True, default="")   # 电话，可选，索引
    id_number = models.CharField(max_length=32, unique=True, null=True, blank=True)   # 身份证号，唯一，可选
    address = models.CharField(max_length=255, blank=True, default="")   # 住址，可选
    emergency_contact = models.CharField(max_length=64, blank=True, default="")   # 紧急联系人姓名，可选
    emergency_phone = models.CharField(max_length=32, blank=True, default="")   # 紧急联系人电话，可选
    blood_type = models.CharField(max_length=8, blank=True, default="")   # 血型，可选

    allergy_history = models.TextField(blank=True, default="")   # 过敏史，可选
    medical_history = models.TextField(blank=True, default="")   # 既往病史，可选

    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return f"{self.patient_no} - {self.name}"   # 返回患者编号和患者姓名


class Visit(models.Model):  
    STATUS_CHOICES = [   # 就诊状态，可选
        ("open", "Open"),   # 开放
        ("closed", "Closed"),   # 关闭
        ("cancelled", "Cancelled"),   # 取消
    ]

    visit_no = models.CharField(max_length=32, unique=True)   # 就诊编号，唯一
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="visits")   # 患者，外键
    doctor = models.ForeignKey('staff.StaffProfile', on_delete=models.PROTECT, related_name="visits", null=True, blank=True)   # 医生，外键，可选
    department = models.CharField(max_length=64, blank=True, default="")   # 就诊科室，可选

    visit_time = models.DateTimeField()   # 就诊时间
    chief_complaint = models.TextField(blank=True, default="")   # 主诉，可选
    diagnosis = models.TextField(blank=True, default="")   # 诊断，可选
    notes = models.TextField(blank=True, default="")   # 备注，可选
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="open")   # 就诊状态，可选
    next_visit_date = models.DateField(null=True, blank=True)   # 建议复诊日期，可选

    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return f"{self.visit_no} ({self.patient.name})"   # 返回就诊编号和患者姓名
