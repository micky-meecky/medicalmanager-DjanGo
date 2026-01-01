# 登录认证系统使用说明

## 概述

本系统实现了基于角色的登录认证系统，支持以下角色：
- **患者（Patient）**：可以查看和编辑个人信息、查看就诊记录、查看处方、查看账单/发票、预约挂号
- **医生（Doctor）**：可以管理患者、开具处方、查看就诊记录
- **药剂师（Pharmacist）**：可以管理药品、库存、发药
- **财务（Finance）**：可以管理发票、支付记录、财务统计
- **管理员（Admin）**：可以访问所有功能

## 功能特性

### 1. 登录系统
- 统一的登录页面：`/login/`
- 支持患者和职工登录
- 自动根据角色重定向到对应的仪表板

### 2. 角色权限控制
- 使用装饰器 `@role_required('doctor', 'admin')` 保护视图
- 自动检查用户角色和状态
- 未授权访问会重定向并显示错误消息

### 3. 仪表板
每个角色都有专属的仪表板：
- `/dashboard/patient/` - 患者仪表板
- `/dashboard/doctor/` - 医生仪表板
- `/dashboard/pharmacist/` - 药剂师仪表板
- `/dashboard/finance/` - 财务仪表板
- `/dashboard/admin/` - 管理员仪表板

## 使用方法

### 创建用户账号

#### 创建患者账号
```python
from django.contrib.auth.models import User
from patients.models import Patient

# 创建用户
user = User.objects.create_user(
    username='patient001',
    password='123456',
    email='patient@example.com'
)

# 创建患者档案并关联用户
patient = Patient.objects.create(
    user=user,
    patient_no='P00001',
    name='张三',
    gender='M',
    # ... 其他字段
)
```

#### 创建职工账号
```python
from django.contrib.auth.models import User
from staff.models import StaffProfile

# 创建用户
user = User.objects.create_user(
    username='doctor001',
    password='123456',
    email='doctor@example.com'
)

# 创建职工档案并关联用户
staff = StaffProfile.objects.create(
    user=user,
    staff_no='D001',
    name='李医生',
    role='doctor',
    department='内科',
    # ... 其他字段
)
```

### 使用装饰器保护视图

```python
from staff.decorators import role_required

# 只允许医生访问
@role_required('doctor')
def doctor_view(request):
    ...

# 允许多个角色访问
@role_required('doctor', 'admin')
def admin_or_doctor_view(request):
    ...

# 只允许患者访问
@role_required('patient')
def patient_view(request):
    ...
```

### 获取用户角色和档案

```python
from staff.decorators import get_user_role, get_user_profile

def my_view(request):
    role = get_user_role(request.user)
    profile = get_user_profile(request.user)
    
    if role == 'patient':
        patient = profile
        # 使用患者信息
    elif role == 'doctor':
        doctor = profile
        # 使用医生信息
```

## 测试账号

运行 `python manage.py seed_demo --reset` 后，会自动创建以下测试账号：

**所有账号的默认密码都是：`123456`**

### 医生账号（Doctor）
- 用户名：`staff_d001`，密码：`123456`（张医生 - 内科 - 主任医师）
- 用户名：`staff_d002`，密码：`123456`（李医生 - 外科 - 副主任医师）
- 用户名：`staff_d003`，密码：`123456`（王医生 - 儿科 - 主治医师）
- 用户名：`staff_d004`，密码：`123456`（刘医生 - 妇科 - 主治医师）

### 财务账号（Finance）
- 用户名：`staff_f001`，密码：`123456`（陈财务 - 财务科）
- 用户名：`staff_f002`，密码：`123456`（赵财务 - 财务科）

### 药剂师账号（Pharmacist）
- 用户名：`staff_p001`，密码：`123456`（周药师 - 药房 - 主管药师）
- 用户名：`staff_p002`，密码：`123456`（吴药师 - 药房 - 药师）

### 管理员账号（Admin）
- 用户名：`staff_a001`，密码：`123456`（管理员 - 行政）

### 患者账号（Patient）
**注意**：患者账号是随机创建的（约30%概率），格式为 `patient_p00001`、`patient_p00002` 等。

运行 `python manage.py seed_demo --reset` 后，可以查看创建了哪些患者账号：

```bash
python manage.py shell
```

然后在 shell 中执行：
```python
from django.contrib.auth.models import User
from patients.models import Patient

# 查看所有有登录账号的患者
patients_with_account = Patient.objects.filter(user__isnull=False)
for p in patients_with_account:
    print(f"患者：{p.name}，用户名：{p.user.username}，密码：123456")
```

或者直接在数据库中查询：
```sql
SELECT u.username, p.name, p.patient_no 
FROM auth_user u 
JOIN patients_patient p ON u.id = p.user_id;
```

## URL 路由

### 认证相关
- `/login/` - 登录页面
- `/logout/` - 登出（自动重定向到登录页）
- `/dashboard/` - 主仪表板（根据角色自动重定向）

### 仪表板
- `/dashboard/patient/` - 患者仪表板
- `/dashboard/doctor/` - 医生仪表板
- `/dashboard/pharmacist/` - 药剂师仪表板
- `/dashboard/finance/` - 财务仪表板
- `/dashboard/admin/` - 管理员仪表板

### 患者专用功能
- `/patient/profile/edit/` - 编辑个人信息
- `/patient/visits/` - 查看所有就诊记录
- `/patient/prescriptions/` - 查看所有处方
- `/patient/prescriptions/<id>/` - 查看处方详情
- `/patient/invoices/` - 查看所有账单/发票
- `/patient/invoices/<id>/` - 查看账单详情

## 注意事项

1. **患者登录**：Patient 模型的 `user` 字段是可选的，只有需要登录的患者才需要关联 User
2. **职工登录**：所有职工（StaffProfile）都必须关联 User
3. **权限检查**：使用 `@role_required` 装饰器时，会自动检查用户是否登录和是否有相应角色
4. **状态检查**：职工账号如果 `is_active=False`，将无法登录
5. **自动重定向**：登录后会自动根据角色重定向到对应的仪表板

## 扩展功能

### 添加新角色
1. 在 `StaffProfile.ROLE_CHOICES` 中添加新角色
2. 创建对应的仪表板视图和模板
3. 在 `dashboard()` 视图中添加重定向逻辑

### 自定义权限
可以在 `staff/decorators.py` 中的 `role_required` 装饰器中添加更复杂的权限检查逻辑。

## 患者功能说明

### 患者登录后可用的功能

1. **个人信息管理**
   - 查看个人信息（姓名、编号、性别、年龄、电话、血型、过敏史、既往病史等）
   - 编辑个人信息（可修改电话、地址、紧急联系人、血型、过敏史、既往病史）

2. **就诊记录**
   - 查看所有就诊记录列表
   - 查看就诊详情（就诊时间、科室、医生、主诉、诊断、状态等）

3. **处方管理**
   - 查看所有处方列表
   - 查看处方详情（处方编号、开方医生、开具时间、发药时间、状态）
   - 查看处方药品明细（药品名称、规格、数量、单价、用法用量）

4. **账单/发票管理**
   - 查看所有账单列表
   - 查看账单详情（发票编号、总金额、状态、开票时间）
   - 查看支付记录（支付时间、金额、方式、收款人）

5. **统计信息**
   - 仪表板显示：就诊总数、处方总数、账单总数、待支付数量

### 患者账号创建

患者账号有两种创建方式：

1. **自动创建**（推荐）：
   ```bash
   python manage.py seed_demo --reset
   ```
   约30%的患者会自动创建登录账号，用户名格式：`patient_p00001`、`patient_p00002` 等

2. **手动创建**：
   在 Django shell 中：
   ```python
   from django.contrib.auth.models import User
   from patients.models import Patient
   
   # 创建用户
   user = User.objects.create_user(
       username='patient001',
       password='123456',
       email='patient001@example.com'
   )
   
   # 关联到现有患者或创建新患者
   patient = Patient.objects.get(patient_no='P00001')  # 或创建新患者
   patient.user = user
   patient.save()
   ```

