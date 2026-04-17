# 企业员工管理系统（UserBack）

基于 **FastAPI + SQLAlchemy + OpenGauss** 的企业员工管理系统后端，支持员工、部门、职位的增删改查及条件查询。

## 技术栈

| 层次 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.x |
| 数据库 | OpenGauss（PostgreSQL 协议兼容） |
| 数据库驱动 | psycopg2-binary |
| 数据校验 | Pydantic v2 |
| ASGI 服务器 | Uvicorn |

## 项目结构

```
UserBack/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口，注册路由
│   ├── database.py          # 数据库连接与会话管理
│   ├── models.py            # SQLAlchemy ORM 模型（Employee, Department, Position）
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── crud.py              # CRUD 操作封装
│   └── routers/
│       ├── __init__.py
│       ├── employee.py      # 员工路由
│       ├── department.py    # 部门路由
│       └── position.py      # 职位路由
├── requirement.txt          # Python 依赖
├── api介绍.md               # API 接口文档
├── 技术选型.md              # 技术选型说明
└── README.md
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- OpenGauss 或 PostgreSQL 数据库

### 2. 创建数据库

连接到 OpenGauss / PostgreSQL，创建数据库：

```sql
CREATE DATABASE employee_db;
```

### 3. 安装依赖

```bash
pip install -r requirement.txt
```

### 4. 配置数据库连接

编辑 `app/database.py` 中的连接字符串，根据实际情况修改用户名、密码、主机和端口：

```python
DATABASE_URL = "postgresql+psycopg2://用户名:密码@主机:端口/employee_db"
```

> 注意：密码中的特殊字符（如 `@`）需要 URL 编码（`@` → `%40`）。

### 5. 启动服务

在项目根目录下运行：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后：
- API 服务：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

> 首次启动会自动创建数据表（`departments`、`positions`、`employees`）。

## E-R 模型

```
┌─────────────┐       1:N       ┌─────────────┐       N:1       ┌─────────────┐
│ Department  │◄───────────────│  Employee   │───────────────►│  Position   │
│─────────────│                │─────────────│                │─────────────│
│ id (PK)     │                │ id (PK)     │                │ id (PK)     │
│ name        │                │ name        │                │ title       │
│ description │                │ gender      │                │ description │
│ created_at  │                │ birth_date  │                │ min_salary  │
└─────────────┘                │ phone       │                │ max_salary  │
                               │ email       │                └─────────────┘
                               │ hire_date   │
                               │ salary      │
                               │ dept_id(FK) │
                               │ pos_id(FK)  │
                               └─────────────┘
```

## API 接口

### 部门管理 `/departments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/departments` | 获取所有部门 |
| GET | `/departments/{id}` | 根据 ID 获取部门 |
| POST | `/departments` | 新增部门 |
| PUT | `/departments/{id}` | 修改部门 |
| DELETE | `/departments/{id}` | 删除部门 |

### 职位管理 `/positions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/positions` | 获取所有职位 |
| GET | `/positions/{id}` | 根据 ID 获取职位 |
| POST | `/positions` | 新增职位 |
| PUT | `/positions/{id}` | 修改职位 |
| DELETE | `/positions/{id}` | 删除职位 |

### 员工管理 `/employees`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/employees` | 获取所有员工（支持按姓名、部门、职位筛选） |
| GET | `/employees/{id}` | 根据 ID 获取员工 |
| POST | `/employees` | 新增员工 |
| PUT | `/employees/{id}` | 修改员工 |
| DELETE | `/employees/{id}` | 删除员工 |

**查询参数：**

```
GET /employees?name=张&department_id=1&position_id=2
```

### 请求/响应示例

**创建员工：**

```bash
curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "gender": "男",
    "birth_date": "1995-06-15",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "hire_date": "2023-03-01",
    "salary": 18000.00,
    "department_id": 1,
    "position_id": 2
  }'
```

**响应约定：**

| 场景 | HTTP 状态码 |
|------|------------|
| 查询/更新成功 | 200 |
| 创建成功 | 201 |
| 资源不存在 | 404 |
| 参数校验失败 | 422 |

## License

MIT