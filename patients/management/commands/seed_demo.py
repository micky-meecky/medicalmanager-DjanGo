import random
import string
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from patients.models import Patient, Visit
from pharmacy.models import Drug, Inventory, Prescription, PrescriptionItem
from finance.models import Invoice, Payment
from staff.models import StaffProfile


# =========================
# 1) 中国身份证 18位生成（含校验位）
# =========================
# 常见地区码（真实存在的行政区划前6位的一部分）
AREA_CODES = [
    "110101",  # 北京 东城
    "110105",  # 北京 朝阳
    "310101",  # 上海 黄浦
    "440106",  # 广州 天河
    "440305",  # 深圳 南山
    "510104",  # 成都 锦江
    "510107",  # 成都 武侯
    "330106",  # 杭州 西湖
    "320102",  # 南京 玄武
    "420106",  # 武汉 武昌
]

WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CHECK_MAP = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]


def _calc_id_check_digit(id17: str) -> str:
    s = sum(int(id17[i]) * WEIGHTS[i] for i in range(17))
    return CHECK_MAP[s % 11]


def gen_cn_id18(birth: date) -> str:
    area = random.choice(AREA_CODES)
    birth_str = birth.strftime("%Y%m%d")
    seq = f"{random.randint(1, 999):03d}"  # 顺序码
    id17 = area + birth_str + seq
    return id17 + _calc_id_check_digit(id17)


# =========================
# 2) 其他“合理数据”生成
# =========================
LAST_NAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜")
GIVEN_1 = list("一二三四五六七八九十子小大文国明强军磊超伟芳娜敏静丽婷涛勇峰杰晨宇")
GIVEN_2 = list("轩涵航昊然博宇子涵思雨欣怡梓轩浩宇雨桐子墨亦凡佳怡")


def gen_name() -> str:
    ln = random.choice(LAST_NAMES)
    if random.random() < 0.7:
        return ln + random.choice(GIVEN_2)
    return ln + random.choice(GIVEN_1) + random.choice(GIVEN_1)


def gen_phone() -> str:
    prefix = random.choice(["130", "131", "132", "133", "135", "136", "137", "138", "139",
                            "150", "151", "152", "155", "156", "157", "158", "159",
                            "170", "171", "173", "175", "176", "177", "178",
                            "180", "181", "182", "183", "185", "186", "187", "188", "189",
                            "191", "198", "199"])
    return prefix + "".join(random.choice(string.digits) for _ in range(8))


def gen_address() -> str:
    """生成地址"""
    cities = ["北京市", "上海市", "广州市", "深圳市", "成都市", "杭州市", "南京市", "武汉市"]
    districts = ["朝阳区", "海淀区", "天河区", "南山区", "锦江区", "西湖区", "玄武区", "武昌区"]
    streets = ["中山路", "解放路", "人民路", "建设路", "和平路", "光明路", "胜利路", "新华路"]
    return f"{random.choice(cities)}{random.choice(districts)}{random.choice(streets)}{random.randint(1, 999)}号"


def gen_blood_type() -> str:
    """生成血型"""
    return random.choice(["A", "B", "AB", "O", ""])  # 可能为空


def gen_department() -> str:
    """生成科室"""
    return random.choice([
        "内科", "外科", "儿科", "妇科", "骨科", "眼科", "耳鼻喉科",
        "皮肤科", "神经内科", "心血管内科", "消化内科", "呼吸内科", "内分泌科"
    ])


def random_birth(min_age=18, max_age=75) -> date:
    today = date.today()
    age = random.randint(min_age, max_age)
    # 在该年龄附近再随机天数，避免全是同一天生日
    delta_days = random.randint(0, 365)
    b = today - timedelta(days=age * 365 + delta_days)
    # 修正非法日期（极少情况）
    return date(b.year, min(b.month, 12), min(b.day, 28))


def gen_patient_no(i: int) -> str:
    return f"P{(i + 1):05d}"


def gen_visit_no(i: int) -> str:
    return f"V{(i + 1):06d}"


def gen_rx_no(i: int) -> str:
    return f"RX{(i + 1):06d}"


def gen_inv_no(i: int) -> str:
    return f"INV{(i + 1):06d}"


# =========================
# 3) 真实常用药品字典（示例）
# =========================
# code, name, spec, unit, sale_price, manufacturer, category, prescription_required
DRUG_CATALOG = [
    ("D001", "阿莫西林胶囊", "0.25g*24粒", "盒", 12.50, "国药集团", "抗生素", True),
    ("D002", "对乙酰氨基酚片", "0.5g*20片", "盒", 6.80, "白云山", "解热镇痛", False),
    ("D003", "布洛芬缓释胶囊", "0.3g*20粒", "盒", 14.90, "扬子江药业", "解热镇痛", False),
    ("D004", "二甲双胍片", "0.5g*30片", "盒", 9.90, "华海药业", "内分泌", True),
    ("D005", "格列美脲片", "2mg*30片", "盒", 18.00, "赛诺菲", "内分泌", True),
    ("D006", "阿托伐他汀钙片", "20mg*7片", "盒", 26.00, "辉瑞", "心血管", True),
    ("D007", "氯雷他定片", "10mg*12片", "盒", 11.00, "西安杨森", "抗过敏", False),
    ("D008", "奥美拉唑肠溶胶囊", "20mg*14粒", "盒", 19.90, "阿斯利康", "消化系统", True),
    ("D009", "头孢克肟胶囊", "0.1g*12粒", "盒", 24.00, "齐鲁制药", "抗生素", True),
    ("D010", "蒙脱石散", "3g*10袋", "盒", 15.50, "博福-益普生", "消化系统", False),
]


def gen_drug_category() -> str:
    """生成药品分类"""
    return random.choice([
        "抗生素", "解热镇痛", "心血管", "内分泌", "抗过敏", 
        "消化系统", "呼吸系统", "神经系统", "皮肤科", "其他"
    ])


def gen_location() -> str:
    """生成存放位置/货架号"""
    areas = ["A", "B", "C", "D"]
    shelves = [str(i) for i in range(1, 21)]
    return f"{random.choice(areas)}区{random.choice(shelves)}号货架"


COMMON_DIAGNOSIS = [
    ("上呼吸道感染", "发热咳嗽、咽痛、鼻塞流涕"),
    ("急性胃肠炎", "腹泻腹痛、恶心呕吐"),
    ("2型糖尿病随访", "血糖控制评估与用药调整"),
    ("高脂血症随访", "血脂评估与用药调整"),
    ("过敏性鼻炎", "鼻痒喷嚏、流清涕"),
]

DOSAGE_TEMPLATES = [
    "每日2次，每次1片",
    "每日3次，每次1片",
    "每日1次，每次1片",
    "必要时服用，每次1片",
    "每日2次，每次1粒",
]

# 职工数据模板
STAFF_TEMPLATES = [
    # (staff_no, name, role, department, position, specialty)
    ("D001", "张医生", "doctor", "内科", "主任医师", "心血管内科"),
    ("D002", "李医生", "doctor", "外科", "副主任医师", "普外科"),
    ("D003", "王医生", "doctor", "儿科", "主治医师", "小儿内科"),
    ("D004", "刘医生", "doctor", "妇科", "主治医师", "妇科"),
    ("F001", "陈财务", "finance", "财务科", "财务专员", ""),
    ("F002", "赵财务", "finance", "财务科", "财务专员", ""),
    ("P001", "周药师", "pharmacist", "药房", "主管药师", ""),
    ("P002", "吴药师", "pharmacist", "药房", "药师", ""),
    ("A001", "管理员", "admin", "行政", "系统管理员", ""),
]


class Command(BaseCommand):
    help = "Seed demo data for MedicalManager (patients/visits/prescriptions/inventory/invoices/payments)."

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=20, help="Number of patients to create (default: 20)")
        parser.add_argument("--reset", action="store_true", help="Delete existing business data before seeding")
        parser.add_argument("--paid-rate", type=float, default=0.7, help="Probability invoice is paid (0~1)")

    @transaction.atomic
    def handle(self, *args, **options):
        n = int(options["n"])
        reset = bool(options["reset"])
        paid_rate = float(options["paid_rate"])

        if reset:
            # 按依赖倒序清理（避免外键保护阻止删除）
            Payment.objects.all().delete()
            Invoice.objects.all().delete()
            PrescriptionItem.objects.all().delete()
            Prescription.objects.all().delete()
            Inventory.objects.all().delete()
            Drug.objects.all().delete()
            Visit.objects.all().delete()
            Patient.objects.all().delete()
            StaffProfile.objects.all().delete()
            # 注意：不删除 User，因为可能有其他用途
            self.stdout.write(self.style.WARNING("Existing business data deleted."))

        # 0) 确保职工存在
        staff_map = {}
        doctor_list = []
        finance_list = []
        
        for staff_no, name, role, dept, position, specialty in STAFF_TEMPLATES:
            # 创建或获取 User
            username = f"staff_{staff_no.lower()}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    email=f"{username}@hospital.com",
                    first_name=name,
                    is_staff=True,
                    is_active=True,
                ),
            )
            if not user.check_password("123456"):  # 默认密码
                user.set_password("123456")
                user.save()
            
            # 创建或获取 StaffProfile
            staff, _ = StaffProfile.objects.get_or_create(
                staff_no=staff_no,
                defaults=dict(
                    user=user,
                    name=name,
                    role=role,
                    department=dept,
                    position=position,
                    specialty=specialty,
                    phone=gen_phone(),
                    email=f"{username}@hospital.com",
                    address=gen_address() if random.random() < 0.5 else "",
                    hire_date=date.today() - timedelta(days=random.randint(365, 3650)),  # 1-10年前入职
                    is_active=True,
                ),
            )
            staff_map[staff_no] = staff
            
            if role == "doctor":
                doctor_list.append(staff)
            elif role == "finance":
                finance_list.append(staff)
        
        self.stdout.write(self.style.SUCCESS(f"Staff ready: {StaffProfile.objects.count()} (doctors: {len(doctor_list)}, finance: {len(finance_list)})"))

        # 1) 确保药品与库存存在
        drug_map = {}
        for code, name, spec, unit, sale_price, mfr, category, rx_required in DRUG_CATALOG:
            # 计算采购价格（约为售价的60-80%）
            purchase_price = round(float(sale_price) * random.uniform(0.6, 0.8), 2)
            
            drug, _ = Drug.objects.get_or_create(
                drug_code=code,
                defaults=dict(
                    name=name,
                    category=category,
                    specification=spec,
                    unit=unit,
                    purchase_price=purchase_price,
                    sale_price=sale_price,
                    manufacturer=mfr,
                    prescription_required=rx_required,
                    description=f"{name}，用于相关疾病的治疗。",
                    is_active=True,
                ),
            )
            drug_map[code] = drug

            inv, created = Inventory.objects.get_or_create(
                drug=drug,
                defaults=dict(
                    quantity=random.randint(200, 600), 
                    warning_level=20,
                    location=gen_location(),
                ),
            )
            # 如果已有库存，保证有足够数量（防止之后扣负）
            if not created and inv.quantity < 200:
                inv.quantity = 200
                inv.save(update_fields=["quantity"])
            # 如果已有库存但没有位置，添加位置
            if not created and not inv.location:
                inv.location = gen_location()
                inv.save(update_fields=["location"])

        self.stdout.write(self.style.SUCCESS(f"Drugs ready: {Drug.objects.count()}, inventories ready: {Inventory.objects.count()}"))

        # 2) 造患者、就诊、处方、账单、支付
        created_patients = 0
        created_visits = 0
        created_rx = 0
        created_inv = 0
        created_paid = 0

        now = timezone.now()

        for i in range(n):
            # Patient
            birth = random_birth()
            pid = gen_cn_id18(birth)
            patient_no = gen_patient_no(i)

            # 避免 unique 冲突（万一你之前手动录过 P00001）
            if Patient.objects.filter(patient_no=patient_no).exists():
                patient_no = f"P{random.randint(10000, 99999)}"

            # 生成紧急联系人信息（70%概率有紧急联系人）
            has_emergency = random.random() < 0.7
            emergency_contact = gen_name() if has_emergency else ""
            emergency_phone = gen_phone() if has_emergency else ""
            
            patient = Patient.objects.create(
                patient_no=patient_no,
                name=gen_name(),
                gender=random.choice(["M", "F"]),
                date_of_birth=birth,
                phone=gen_phone(),
                id_number=pid,
                address=gen_address() if random.random() < 0.8 else "",  # 80%概率有地址
                emergency_contact=emergency_contact,
                emergency_phone=emergency_phone,
                blood_type=gen_blood_type(),
                allergy_history=random.choice(["无", "青霉素过敏", "海鲜过敏", "无明显过敏史"]),
                medical_history=random.choice(["无", "2型糖尿病", "高血压", "脂肪肝", "无"]),
            )
            created_patients += 1

            # Visit（给每个患者生成 1~2 次就诊）
            visit_count = 1 if random.random() < 0.7 else 2
            for j in range(visit_count):
                v_index = i * 2 + j
                visit_no = gen_visit_no(v_index)
                if Visit.objects.filter(visit_no=visit_no).exists():
                    visit_no = f"V{random.randint(100000, 999999)}"

                dx, cc = random.choice(COMMON_DIAGNOSIS)
                visit_time = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
                
                # 生成复诊日期（30%概率有复诊，在就诊后7-30天）
                next_visit = None
                if random.random() < 0.3:
                    next_visit = (visit_time + timedelta(days=random.randint(7, 30))).date()

                # 随机选择一个医生
                doctor = random.choice(doctor_list) if doctor_list else None
                
                visit = Visit.objects.create(
                    visit_no=visit_no,
                    patient=patient,
                    doctor=doctor,
                    department=gen_department(),
                    visit_time=visit_time,
                    chief_complaint=cc,
                    diagnosis=dx,
                    notes="系统自动生成测试数据",
                    status="closed",
                    next_visit_date=next_visit,
                )
                created_visits += 1

                # Prescription
                rx_no = gen_rx_no(v_index)
                if Prescription.objects.filter(prescription_no=rx_no).exists():
                    rx_no = f"RX{random.randint(100000, 999999)}"

                # 生成开具时间（就诊时间后几分钟）
                issued_time = visit_time + timedelta(minutes=random.randint(5, 30))
                
                # 使用就诊的医生或随机选择一个医生作为开方医生
                rx_doctor = visit.doctor or (random.choice(doctor_list) if doctor_list else None)
                
                rx = Prescription.objects.create(
                    prescription_no=rx_no,
                    visit=visit,
                    doctor=rx_doctor,
                    status="issued",
                    notes=random.choice(["", "注意饮食", "多休息", "按时服药", ""]),
                    issued_at=issued_time,
                )
                created_rx += 1

                # PrescriptionItems：1~3种药
                drug_choices = random.sample(list(drug_map.values()), k=random.randint(1, 3))
                total = 0

                for d in drug_choices:
                    qty = random.randint(1, 3)
                    price = float(d.sale_price)
                    total += price * qty

                    # 扣库存（确保不负）
                    inv = d.inventory
                    if inv.quantity < qty:
                        inv.quantity += 200
                    inv.quantity -= qty
                    inv.save(update_fields=["quantity"])

                    PrescriptionItem.objects.create(
                        prescription=rx,
                        drug=d,
                        quantity=qty,
                        unit_price=d.sale_price,
                        dosage=random.choice(DOSAGE_TEMPLATES),
                        notes=random.choice(["", "饭后服用", "饭前服用", "注意不良反应", ""]),
                    )

                # 标记已发药
                dispensed_time = issued_time + timedelta(minutes=random.randint(10, 60))
                rx.status = "dispensed"
                rx.dispensed_at = dispensed_time
                rx.save(update_fields=["status", "dispensed_at"])

                # Invoice
                inv_no = gen_inv_no(v_index)
                if Invoice.objects.filter(invoice_no=inv_no).exists():
                    inv_no = f"INV{random.randint(100000, 999999)}"

                # 生成开票时间（处方发药后几分钟）
                invoice_issued_time = dispensed_time + timedelta(minutes=random.randint(5, 20))
                finance_person = random.choice(finance_list) if finance_list else None

                invoice = Invoice.objects.create(
                    invoice_no=inv_no,
                    visit=visit,
                    patient=patient,
                    issued_by=finance_person,
                    total_amount=round(total, 2),
                    status="unpaid",
                    notes=random.choice(["", "请妥善保管发票", ""]),
                    issued_at=invoice_issued_time,
                )
                created_inv += 1

                # Payment（按概率生成已支付）
                if random.random() < paid_rate:
                    method = random.choice(["cash", "card", "online"])
                    paid_time = invoice_issued_time + timedelta(minutes=random.randint(1, 30))
                    
                    Payment.objects.create(
                        invoice=invoice,
                        amount=invoice.total_amount,
                        method=method,
                        received_by=finance_person,
                        note="系统自动生成测试支付",
                    )
                    invoice.status = "paid"
                    invoice.paid_at = paid_time
                    invoice.save(update_fields=["status", "paid_at"])
                    created_paid += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed done. patients={created_patients}, visits={created_visits}, prescriptions={created_rx}, invoices={created_inv}, paid={created_paid}"
        ))

