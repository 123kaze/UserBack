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

## 遇到的问题

### 问题：VS Code Remote-SSH 连接远程服务器失败

**现象：** 使用 VScode IDE 的 Remote-SSH 功能连接远程 Linux 服务器时，反复弹出密码框，或者连接后立即断开，日志中出现如下错误：

```
channel 3: open failed: administratively prohibited: open failed
Error while creating SOCKS connection Error: Socket closed
```

**背景知识：** VS Code 的 Remote-SSH 工作原理分为三步：

1. **SSH 认证**：本地 IDE 通过 SSH 协议连接到远程服务器（公钥认证或密码认证）
2. **安装远程服务端**：认证成功后，IDE 会在远程服务器的 `~/.vscode-server/` 目录下安装一个后台服务进程
3. **端口转发**：IDE 通过 SSH 的 **TCP 端口转发**（`-D` 参数，SOCKS 代理）将本地端口映射到远程服务端口，实现本地 IDE 与远程服务端的双向通信

其中第 3 步依赖 SSH 服务端的 **TCP 转发功能**。如果服务端禁用了此功能，IDE 虽然能认证成功，但无法建立数据通道，导致连接失败。

**根因：** 远程服务器的 SSH 配置文件 `/etc/ssh/sshd_config` 中禁用了 TCP 转发：

```bash
AllowTcpForwarding no   # 禁止 TCP 端口转发（Windsurf 必需）
GatewayPorts no         # 禁止网关端口
PermitTunnel no         # 禁止隧道
```

这是很多云服务器（如华为云 openEuler）的**默认安全策略**，出于安全考虑默认关闭了转发功能。

**解决方法：** 修改远程服务器的 `/etc/ssh/sshd_config`，启用 TCP 转发：

```bash
# 编辑 sshd 配置
sudo vi /etc/ssh/sshd_config

# 找到以下配置项，改为 yes（如果没有则添加到文件末尾）
AllowTcpForwarding yes
GatewayPorts yes
PermitTunnel yes

# 重启 sshd 使配置生效
sudo systemctl restart sshd
```

> **安全提示：** 开启 TCP 转发会允许 SSH 用户创建端口转发隧道。在生产环境中，建议仅对特定用户开启，而非全局开启。

---

### 问题：SSH 密钥认证 vs 密码认证混淆

**现象：** SSH 连接时反复弹出密码框，输入正确密码后仍然认证失败。

**根因：** SSH 私钥文件（如 `~/.ssh/id_rsa`、`~/.ssh/id_ed25519`）设置了 **passphrase（密码短语）** 保护。当 IDE 弹出密码框时，它可能在请求：

- **密钥的 passphrase**（用于解密本地私钥文件）
- **服务器的登录密码**（用于密码认证）

这两者容易混淆。如果服务器的 `authorized_keys` 中没有你的公钥，SSH 会回退到密码认证，而你输入的 passphrase 会被当作服务器密码，导致认证失败。

**解决方法：** 将本地公钥部署到远程服务器，实现免密码登录：

```bash
# 方法 1：使用 ssh-copy-id（Linux/macOS）
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@服务器IP

# 方法 2：手动复制（Windows 或无 ssh-copy-id 时）
# 查看本地公钥
cat ~/.ssh/id_ed25519.pub

# 登录远程服务器，将公钥追加到 authorized_keys
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

部署公钥后，SSH 会自动使用密钥认证，不再需要输入服务器密码。如果私钥有 passphrase，可以使用 `ssh-agent` 缓存，避免每次都输入：

```bash
# 启动 ssh-agent 并添加密钥（输入一次 passphrase 后会缓存）
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
```

---

### 问题排查思路总结

遇到 Remote-SSH 连不上时，按以下顺序排查：

1. **网络层**：`ping 服务器IP` 或 `Test-NetConnection -ComputerName IP -Port 22` 确认端口可达
2. **认证层**：`ssh -v user@host` 查看详细认证过程，确认是密钥认证还是密码认证
3. **转发层**：检查 `/etc/ssh/sshd_config` 中的 `AllowTcpForwarding` 是否为 `yes`
4. **服务端层**：检查远程 `~/.windsurf-server/` 目录下的日志，确认 IDE 服务端是否正常启动

## License

MIT