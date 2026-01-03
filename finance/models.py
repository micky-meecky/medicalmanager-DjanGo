from django.db import models
from patients.models import Visit, Patient


"""
    本模块 `finance/models.py` 定义了与财务管理、发票管理和支付管理相关的数据模型，适用于医疗管理系统的财务管理功能。

    主要内容如下：

    1. Invoice（发票）模型
    --------------------
    用于存储每次就诊的发票信息。其属性包括：
    - `invoice_no`：发票编号，唯一，用于区分不同发票。
    - `visit`：关联的就诊记录（一对一关系，保护删除），一个就诊记录对应一个发票。
    - `patient`：关联的患者（外键，保护删除），一个患者可以有多张发票。
    - `issued_by`：开票人/收款人（外键，保护删除），可选，记录开具发票的财务人员。
    - `total_amount`：总金额，精确到小数点后两位，默认为0。
    - `status`：发票状态，包括未支付（unpaid）、已支付（paid）、已退款（refunded），可由用户选择，默认为"未支付"。
    - `notes`：发票备注，可选，用于记录特殊说明。
    - `issued_at`：开票时间，可选，记录发票开具的时间。
    - `paid_at`：支付完成时间，可选，记录发票完全支付的时间。
    - `created_at`：创建时间，自动记录数据创建时间。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，便于在 Django 管理后台等处直观显示发票编号。

    2. Payment（支付）模型
    ---------------------
    记录每笔发票的支付信息。其属性包括：
    - `invoice`：关联的发票（外键，保护删除），一个发票可以有多笔支付记录。
    - `amount`：支付金额，精确到小数点后两位。
    - `method`：支付方式，包括现金（cash）、刷卡（card）、在线支付（online）、医保（insurance），可由用户选择，默认为"现金"。
    - `received_by`：收款人（外键，保护删除），可选，记录处理该笔支付的财务人员。
    - `paid_at`：支付时间，自动记录支付发生时间。
    - `note`：备注信息，可选，用于记录支付相关的额外说明。
    - `updated_at`：更新时间，自动记录数据最后更新时间。

    该模型实现了 `__str__` 方法，返回发票编号和支付金额，便于识别。

    关系说明
    --------
    - Visit 与 Invoice 为一对一关系（一个就诊记录对应一个发票）。
    - Patient 与 Invoice 为一对多关系（一个患者可以有多张发票）。
    - StaffProfile（财务人员）与 Invoice 为一对多关系（一个财务人员可以开具多张发票）。
    - Invoice 与 Payment 为一对多关系（一个发票可以有多笔支付记录，支持分期支付或多次支付）。
    - StaffProfile（财务人员）与 Payment 为一对多关系（一个财务人员可以处理多笔支付）。

    其他说明
    --------
    - 所有金额字段均使用 DecimalField 类型，精确到小数点后两位，确保财务数据的准确性。
    - 所有文本类字段（如备注等）均允许为空并设置了默认值，保证灵活性和数据完整性。
    - 所有模型字段均给出详细注释，方便维护和理解。
    - 添加了适当的唯一约束，提高数据一致性与查询效率。
    - 支持 Django ORM 的相关特性（如 `auto_now_add`）提升开发便利性。
    - 使用保护删除策略（PROTECT），确保财务数据的安全性和完整性，防止误删重要财务记录。

"""


class Invoice(models.Model):
    STATUS_CHOICES = [   # 发票状态，可选
        ("unpaid", "Unpaid"),   # 未支付
        ("paid", "Paid"),   # 已支付
        ("refunded", "Refunded"),   # 已退款
    ]

    invoice_no = models.CharField(max_length=32, unique=True)   # 发票编号，唯一
    visit = models.OneToOneField(Visit, on_delete=models.PROTECT, related_name="invoice")   # 就诊记录，一对一关系
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="invoices")   # 患者，外键
    issued_by = models.ForeignKey('staff.StaffProfile', on_delete=models.PROTECT, related_name="issued_invoices", null=True, blank=True)   # 开票人，外键，可选

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)   # 总金额
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="unpaid")   # 发票状态，可选
    notes = models.TextField(blank=True, default="")   # 发票备注，可选
    issued_at = models.DateTimeField(null=True, blank=True)   # 开票时间，可选
    paid_at = models.DateTimeField(null=True, blank=True)   # 支付完成时间，可选
    created_at = models.DateTimeField(auto_now_add=True)   # 创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return self.invoice_no   # 返回发票编号


class Payment(models.Model):
    METHOD_CHOICES = [   # 支付方式，可选
        ("wechat", "WeChat Pay"),   # 微信支付
        ("alipay", "Alipay"),   # 支付宝
        ("unionpay", "UnionPay"),   # 银联
        ("visa", "Visa"),   # Visa
        ("mastercard", "Mastercard"),   # 万事达
        ("cash", "Cash"),   # 现金
        ("card", "Card"),   # 刷卡
        ("insurance", "Insurance"),   # 医保
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")   # 发票，外键
    amount = models.DecimalField(max_digits=12, decimal_places=2)   # 支付金额
    method = models.CharField(max_length=16, choices=METHOD_CHOICES, default="wechat")   # 支付方式，可选
    received_by = models.ForeignKey('staff.StaffProfile', on_delete=models.PROTECT, related_name="received_payments", null=True, blank=True)   # 收款人，外键，可选
    paid_at = models.DateTimeField(auto_now_add=True)   # 支付时间，自动添加
    note = models.CharField(max_length=255, blank=True, default="")   # 备注，可选
    updated_at = models.DateTimeField(auto_now=True)   # 更新时间，自动更新

    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.amount}"   # 返回发票编号和支付金额
