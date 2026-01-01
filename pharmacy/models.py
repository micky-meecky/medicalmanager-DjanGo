from django.db import models
from patients.models import Visit


"""
    本模块 `pharmacy/models.py` 定义了与药品管理、库存管理和处方管理相关的数据模型，适用于医疗管理系统的药房管理功能。

    主要内容如下：

    1. Drug（药品）模型
    --------------------
    用于存储药品的基本信息。其属性包括：
    - `drug_code`：药品编码，唯一，用于区分不同药品。
    - `name`：药品名称。
    - `category`：药品分类，可选，如"抗生素"、"解热镇痛"、"心血管"等。
    - `specification`：规格，可选，如"10mg/片"。
    - `unit`：单位，可选，如"盒"、"瓶"、"片"等。
    - `purchase_price`：采购价格/成本价，精确到小数点后两位，用于计算利润。
    - `sale_price`：销售价格，精确到小数点后两位。
    - `manufacturer`：生产厂家，可选。
    - `prescription_required`：是否需要处方，布尔值，用于区分处方药和非处方药。
    - `description`：药品描述/说明，可选。
    - `is_active`：是否启用，布尔值，默认为启用状态。
    - `created_at`：创建时间，自动记录数据创建时间。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，便于在 Django 管理后台等处直观显示药品编码和名称。

    2. Inventory（库存）模型
    ----------------------
    记录每个药品的库存信息。其属性包括：
    - `drug`：关联的药品（一对一关系，级联删除），一个药品对应一个库存记录。
    - `quantity`：当前库存数量，默认为0。
    - `warning_level`：库存预警级别，当库存低于此值时触发预警，默认为10。
    - `location`：存放位置/货架号，可选，用于快速定位药品。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，返回药品名称和库存数量，便于识别。

    3. Prescription（处方）模型
    -------------------------
    记录每次就诊的处方信息。其属性包括：
    - `prescription_no`：处方编号，唯一。
    - `visit`：关联的就诊记录（一对一关系，保护删除），一个就诊记录对应一个处方。
    - `doctor`：关联的开方医生（外键，保护删除），可选，记录开具处方的医生。
    - `status`：处方状态，包括草稿（draft）、已开具（issued）、已发药（dispensed）、已取消（cancelled），可由用户选择，默认为"草稿"。
    - `notes`：处方备注，可选，用于记录特殊说明。
    - `issued_at`：开具时间，可选，记录处方正式开具的时间。
    - `dispensed_at`：发药时间，可选，记录处方发药的时间。
    - `created_at`：创建时间，自动记录。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，返回处方编号，便于识别。

    4. PrescriptionItem（处方项）模型
    ------------------------------
    记录处方中的具体药品项。其属性包括：
    - `prescription`：关联的处方（外键，级联删除），一个处方可以包含多个处方项。
    - `drug`：关联的药品（外键，保护删除）。
    - `quantity`：药品数量。
    - `unit_price`：单价，精确到小数点后两位。
    - `dosage`：用法用量，可选，描述药品的使用方法和剂量。
    - `notes`：备注，可选，用于记录该药品项的特殊说明。
    - `created_at`：创建时间，自动记录。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型在 Meta 类中设置了唯一约束，确保同一处方中不会重复添加相同的药品。
    该模型实现了 `__str__` 方法，返回处方编号和药品名称，便于识别。

    关系说明
    --------
    - Drug 与 Inventory 为一对一关系（一个药品对应一个库存记录）。
    - Visit 与 Prescription 为一对一关系（一个就诊记录对应一个处方）。
    - StaffProfile（医生）与 Prescription 为一对多关系（一个医生可以开具多个处方）。
    - Prescription 与 PrescriptionItem 为一对多关系（一个处方可以包含多个处方项）。
    - PrescriptionItem 与 Drug 为多对一关系（多个处方项可以关联同一个药品）。

    其他说明
    --------
    - 所有文本类字段（如规格、单位、用法用量等）均允许为空并设置了默认值，保证灵活性和数据完整性。
    - 所有模型字段均给出详细注释，方便维护和理解。
    - 添加了适当的唯一约束和索引，提高数据一致性与查询效率。
    - 支持 Django ORM 的相关特性（如 `auto_now_add`、`auto_now`）提升开发便利性。
    - 使用级联删除和保护删除策略，确保数据的完整性和安全性。

    此文件结构清晰、设计合理，可方便地扩展使用于药品管理、库存管理、处方管理等药房业务场景。
"""


class Drug(models.Model):
    drug_code = models.CharField(max_length=32, unique=True)   # 药品编码，唯一
    name = models.CharField(max_length=128)   # 药品名称
    category = models.CharField(max_length=64, blank=True, default="")   # 药品分类，可选
    specification = models.CharField(max_length=128, blank=True, default="")   # 规格，可选
    unit = models.CharField(max_length=32, blank=True, default="")   # 单位，可选

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # 采购价格/成本价
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # 销售价格

    manufacturer = models.CharField(max_length=128, blank=True, default="")   # 生产厂家，可选
    prescription_required = models.BooleanField(default=False)   # 是否需要处方，默认为非处方药
    description = models.TextField(blank=True, default="")   # 药品描述，可选
    is_active = models.BooleanField(default=True)   # 是否启用，默认为启用
    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return f"{self.drug_code} - {self.name}"   # 返回药品编码和药品名称


class Inventory(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE, related_name="inventory")   # 药品，一对一关系
    quantity = models.IntegerField(default=0)   # 当前库存数量
    warning_level = models.IntegerField(default=10)   # 库存预警级别
    location = models.CharField(max_length=64, blank=True, default="")   # 存放位置/货架号，可选
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return f"{self.drug.name}: {self.quantity}"   # 返回药品名称和库存数量


class Prescription(models.Model):
    STATUS_CHOICES = [   # 处方状态，可选
        ("draft", "Draft"),   # 草稿
        ("issued", "Issued"),   # 已开具
        ("dispensed", "Dispensed"),   # 已发药
        ("cancelled", "Cancelled"),   # 已取消
    ]

    prescription_no = models.CharField(max_length=32, unique=True)   # 处方编号，唯一
    visit = models.OneToOneField(Visit, on_delete=models.PROTECT, related_name="prescription")   # 就诊记录，一对一关系
    doctor = models.ForeignKey('staff.StaffProfile', on_delete=models.PROTECT, related_name="prescriptions", null=True, blank=True)   # 开方医生，外键，可选
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")   # 处方状态，可选
    notes = models.TextField(blank=True, default="")   # 处方备注，可选
    issued_at = models.DateTimeField(null=True, blank=True)   # 开具时间，可选
    dispensed_at = models.DateTimeField(null=True, blank=True)   # 发药时间，可选
    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return self.prescription_no   # 返回处方编号


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")   # 处方，外键
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)   # 药品，外键
    quantity = models.IntegerField()   # 药品数量
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # 单价
    dosage = models.CharField(max_length=128, blank=True, default="")   # 用法用量，可选
    notes = models.CharField(max_length=255, blank=True, default="")   # 备注，可选
    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    class Meta:
        unique_together = ("prescription", "drug")   # 确保同一处方中不会重复添加相同的药品

    def __str__(self):
        return f"{self.prescription.prescription_no} - {self.drug.name}"   # 返回处方编号和药品名称
