# 企业员工管理系统 — API 接口文档

> 基础路径：`http://localhost:8000`  
> 数据格式：JSON  
> 启动后可访问自动文档：`http://localhost:8000/docs`

---

## 一、部门管理 `/departments`

| 方法 | 路径 | 说明 | 请求体 | 返回 |
|------|------|------|--------|------|
| GET | `/departments` | 获取所有部门 | 无 | 部门列表 |
| GET | `/departments/{id}` | 根据ID获取部门 | 无 | 单个部门 |
| POST | `/departments` | 新增部门 | `{name, description}` | 创建的部门 |
| PUT | `/departments/{id}` | 修改部门 | `{name, description}` | 更新后的部门 |
| DELETE | `/departments/{id}` | 删除部门 | 无 | `{detail: "删除成功"}` |

**请求体示例（POST/PUT）：**
```json
{
  "name": "技术部",
  "description": "负责产品研发"
}
```

---

## 二、职位管理 `/positions`

| 方法 | 路径 | 说明 | 请求体 | 返回 |
|------|------|------|--------|------|
| GET | `/positions` | 获取所有职位 | 无 | 职位列表 |
| GET | `/positions/{id}` | 根据ID获取职位 | 无 | 单个职位 |
| POST | `/positions` | 新增职位 | `{title, description, min_salary, max_salary}` | 创建的职位 |
| PUT | `/positions/{id}` | 修改职位 | `{title, description, min_salary, max_salary}` | 更新后的职位 |
| DELETE | `/positions/{id}` | 删除职位 | 无 | `{detail: "删除成功"}` |

**请求体示例（POST/PUT）：**
```json
{
  "title": "高级工程师",
  "description": "负责核心系统开发",
  "min_salary": 15000.00,
  "max_salary": 30000.00
}
```

---

## 三、员工管理 `/employees`

| 方法 | 路径 | 说明 | 请求体 | 返回 |
|------|------|------|--------|------|
| GET | `/employees` | 获取所有员工 | 无 | 员工列表 |
| GET | `/employees/{id}` | 根据ID获取员工 | 无 | 单个员工（含部门、职位信息） |
| POST | `/employees` | 新增员工 | 见下方 | 创建的员工 |
| PUT | `/employees/{id}` | 修改员工 | 见下方 | 更新后的员工 |
| DELETE | `/employees/{id}` | 删除员工 | 无 | `{detail: "删除成功"}` |

**查询参数（GET 列表可选）：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 按姓名模糊搜索 |
| `department_id` | int | 按部门筛选 |
| `position_id` | int | 按职位筛选 |

示例：`GET /employees?name=张&department_id=1`

**请求体示例（POST/PUT）：**
```json
{
  "name": "张三",
  "gender": "男",
  "birth_date": "1995-06-15",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "hire_date": "2023-03-01",
  "salary": 18000.00,
  "department_id": 1,
  "position_id": 2
}
```

---

## 四、统计查询 `/stats`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/stats/department-count` | 各部门员工人数统计 |
| GET | `/stats/salary-range?min=10000&max=20000` | 按薪资范围查询员工 |

---

## 五、通用约定

- **成功响应**：直接返回数据对象或列表，HTTP 200
- **创建成功**：返回创建的对象，HTTP 201
- **资源不存在**：`{"detail": "xxx不存在"}`，HTTP 404
- **参数错误**：`{"detail": "xxx"}`，HTTP 422（FastAPI 自动校验）
