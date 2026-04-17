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

### 问题：系统默认 Python 被替换后 dnf/yum 无法使用

**现象：** 执行 `dnf` 或 `yum` 命令时报错，无法安装任何软件包。

**背景知识：** openEuler（及 CentOS 8+、RHEL 8+）系统中，`dnf` 和 `yum` 是用 **Python 3** 编写的包管理器。系统默认的 `/usr/bin/python` 是一个**软链接**，通常指向 `python2`。系统中同时存在 Python 2 和 Python 3，各有用途：

```
/usr/bin/python  → python2（系统默认，部分旧脚本依赖）
/usr/bin/python2 → python2.7
/usr/bin/python3 → python3.7
```

**根因：** 之前为了方便使用 Python 3，执行了以下操作：

```bash
cd /usr/bin
mv python python.bak          # 备份原来的 python 软链接
ln -s python3 /usr/bin/python  # 让 python 指向 python3
```

这导致依赖 `python` 命令的系统脚本行为异常。虽然 `dnf` 本身用的是 `python3`，但系统中还有很多脚本（如 `dnf` 的依赖模块路径解析）依赖原始的软链接关系。

**解决方法：** 恢复原始的软链接：

```bash
rm -f /usr/bin/python                  # 删除指向 python3 的错误软链接
mv /usr/bin/python.bak /usr/bin/python # 还原备份
python -V                              # 验证：应输出 Python 2.7.x
```

**最佳实践：** 永远不要修改 `/usr/bin/python` 的指向。如果想方便地使用 Python 3，有以下安全的替代方式：

```bash
# 方式 1：直接用 python3 命令
python3 script.py

# 方式 2：在脚本中指定解释器
#!/usr/bin/env python3

# 方式 3：使用 alias（仅影响当前用户，不影响系统）
echo 'alias python=python3' >> ~/.bashrc
source ~/.bashrc
```

---

### 问题：dnf 报错 `ImportError: libcurl.so.4: symbol SSLv3_client_method`

**现象：** 运行 `dnf` 时出现如下错误：

```
ImportError: /lib64/libcurl.so.4: symbol SSLv3_client_method version OPENSSL_1_1_0
not defined in file libssl.so.1.1 with link time reference
```

**背景知识：** Linux 程序运行时需要加载**动态链接库**（`.so` 文件，类似 Windows 的 `.dll`）。系统通过以下顺序查找 `.so` 文件：

1. `LD_LIBRARY_PATH` 环境变量指定的目录（**最高优先级**）
2. `/etc/ld.so.cache` 缓存（由 `ldconfig` 生成）
3. 默认路径 `/lib64`、`/usr/lib64`

`libcurl`（HTTP 客户端库）依赖 `libssl`（OpenSSL 加密库）。如果加载了**错误版本**的 `libssl`，就会因为缺少符号（函数）而报错。

**根因：** openGauss 安装时在 `/etc/profile` 中添加了一行：

```bash
export LD_LIBRARY_PATH=/opt/software/openGauss/script/gspylib/clib:$LD_LIBRARY_PATH
```

这使得**所有程序**优先加载 openGauss 自带的 `libssl.so.1.1`（位于 `/opt/software/openGauss/script/gspylib/clib/`），而不是系统的 `/lib64/libssl.so.1.1`。openGauss 自带的 OpenSSL 版本较新，移除了 `SSLv3_client_method` 这个已废弃的函数，导致 `libcurl` 找不到它需要的符号。

可以用 `ldd` 命令验证（`ldd` 显示程序实际加载的动态库路径）：

```bash
ldd /lib64/libcurl.so.4 | grep ssl
# 输出：libssl.so.1.1 => /opt/software/openGauss/script/gspylib/clib/libssl.so.1.1
# ↑ 加载了 openGauss 的版本，而不是系统的 /lib64/libssl.so.1.1
```

**解决方法：** 运行 `dnf` 时临时清除 `LD_LIBRARY_PATH`，让它使用系统默认的库：

```bash
# 在命令前加 LD_LIBRARY_PATH="" 临时覆盖环境变量
LD_LIBRARY_PATH="" dnf install <包名> -y

# 示例
LD_LIBRARY_PATH="" dnf install git --nogpgcheck -y
LD_LIBRARY_PATH="" dnf clean packages
```

> **知识点：** `VAR=value command` 是 bash 语法，表示仅在执行 `command` 时临时设置环境变量 `VAR`，不影响当前 shell。

---

### 问题：dnf 安装包时报 `GPG check FAILED`

**现象：**

```
Package perl-TermReadKey-2.38-2.oe1.aarch64.rpm is not signed
Error: GPG check FAILED
```

**背景知识：** Linux 包管理器默认会对下载的 `.rpm` 包进行 **GPG 签名验证**，确保包来自可信的发布者且未被篡改。这是一种安全机制。如果某个包没有签名，验证就会失败。

**根因：** openEuler 的 `update` 仓库中，部分包没有 GPG 签名。

**解决方法：** 安装时加 `--nogpgcheck` 参数跳过签名验证：

```bash
LD_LIBRARY_PATH="" dnf install git --nogpgcheck -y
```

> **安全提示：** 跳过 GPG 检查意味着不验证包的来源和完整性，仅在可信的仓库源上使用。生产环境应尽量保持 GPG 检查开启。

---

### 问题：pip 安装依赖超时

**现象：** 执行 `pip3 install -r requirement.txt` 时报错：

```
ReadTimeoutError: Read timed out.
```

**背景知识：** `pip` 默认从 **PyPI**（Python Package Index，`https://pypi.org`）下载包，其服务器在国外。从国内服务器访问速度很慢，经常超时。

**解决方法：** 使用国内镜像源加速下载：

```bash
# 使用清华大学镜像源（推荐）
pip3 install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 其他常用镜像源：
# 阿里云：https://mirrors.aliyun.com/pypi/simple/
# 中科大：https://pypi.mirrors.ustc.edu.cn/simple/
# 豆瓣：  https://pypi.douban.com/simple/
```

如果想**永久设置**镜像源，避免每次都加 `-i` 参数：

```bash
# 创建 pip 配置文件
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

---

### 问题：OpenGauss 数据库启动失败（内存不足）

**现象：** 以 `omm` 用户执行 `gs_om -t start` 时报错：

```
FATAL: could not create shared memory segment: Cannot allocate memory
DETAIL: Failed system call was shmget(key=26000001, size=1993433088, 03600).
```

**背景知识：** OpenGauss（基于 PostgreSQL）启动时需要分配一块**共享内存（Shared Memory）**，用于：

- **shared_buffers**：数据页缓存，类似数据库的"内存数据库"，越大则磁盘 IO 越少
- **WAL buffers**：预写日志缓冲区
- **连接管理**：每个客户端连接都需要一定的内存

数据库根据配置文件中的参数计算所需的共享内存大小。如果计算出的大小超过了操作系统可用的内存，`shmget()` 系统调用就会失败。

**根因：** 服务器只有 **2.8GB 内存**，但数据库配置文件中的参数是按大内存服务器设置的：

| 参数 | 原值 | 含义 |
|------|------|------|
| `max_process_memory` | 4GB | 数据库进程最大可用内存总量 |
| `shared_buffers` | 256MB | 数据页缓存大小 |
| `bulk_write_ring_size` | 256MB | 批量写入环形缓冲区 |
| `max_connections` | 5000 | 最大并发连接数（每个连接消耗内存） |
| `work_mem` | 64MB | 每个查询操作（排序、哈希）可用的内存 |
| `maintenance_work_mem` | 128MB | 维护操作（VACUUM、CREATE INDEX）的内存 |

这些参数加起来，数据库计算出需要 **1901MB** 共享内存，超过了系统可用内存。

**解决方法：** 编辑数据库配置文件 `/gaussdb/data/db1/postgresql.conf`，降低内存相关参数：

```bash
# 用 sed 命令批量修改（也可以用 vi 手动编辑）
sed -i 's/^max_process_memory = 4GB/max_process_memory = 2GB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^shared_buffers = 256MB/shared_buffers = 128MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^bulk_write_ring_size = 256MB/bulk_write_ring_size = 128MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^max_connections = 5000/max_connections = 200/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^work_mem = 64MB/work_mem = 8MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^maintenance_work_mem = 128MB/maintenance_work_mem = 32MB/' /gaussdb/data/db1/postgresql.conf
```

修改后的值：

| 参数 | 原值 | 新值 | 说明 |
|------|------|------|------|
| `max_process_memory` | 4GB | **2GB** | 不超过物理内存的 70% |
| `shared_buffers` | 256MB | **128MB** | 通常设为内存的 15%-25% |
| `bulk_write_ring_size` | 256MB | **128MB** | 不超过 shared_buffers |
| `max_connections` | 5000 | **200** | 学习环境 200 足够 |
| `work_mem` | 64MB | **8MB** | 按需调整，过大会占用过多内存 |
| `maintenance_work_mem` | 128MB | **32MB** | 维护操作不需要太多内存 |

然后重新启动数据库：

```bash
su - omm -c "gs_om -t start"
```

> **经验法则：** 数据库内存参数应根据服务器的实际物理内存来设置，而不是使用默认值。一般建议 `max_process_memory` 不超过物理内存的 60%-70%，留足空间给操作系统和其他进程。

---

### 问题：Git 克隆私有仓库报 `Permission denied (publickey)`

**现象：**

```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**背景知识：** GitHub 支持两种远程仓库访问方式：

| 方式 | URL 格式 | 认证方式 |
|------|----------|----------|
| SSH | `git@github.com:user/repo.git` | SSH 密钥对 |
| HTTPS | `https://github.com/user/repo.git` | 用户名 + Token |

使用 SSH 方式时，GitHub 需要通过你的 **SSH 公钥** 来验证身份。每台机器都需要生成自己的密钥对，并将公钥添加到 GitHub 账户。

**解决方法：**

```bash
# 1. 生成 SSH 密钥对（一路回车即可）
ssh-keygen -t ed25519 -C "github" -f ~/.ssh/id_ed25519 -N ""

# 2. 查看公钥内容
cat ~/.ssh/id_ed25519.pub
# 输出类似：ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... github

# 3. 将公钥添加到 GitHub
#    打开 https://github.com/settings/keys
#    点击 "New SSH key"，粘贴上面的公钥内容，保存

# 4. 测试连接
ssh -T git@github.com
# 成功输出：Hi username! You've been authenticated...

# 5. 克隆仓库
git clone git@github.com:123kaze/UserBack.git
```

> **知识点：** SSH 密钥对由**私钥**（`id_ed25519`，绝对不能泄露）和**公钥**（`id_ed25519.pub`，可以公开分享）组成。GitHub 用你上传的公钥验证你本地私钥的签名，从而确认你的身份。`ed25519` 是目前推荐的密钥算法，比 RSA 更安全且密钥更短。

---

## License

MIT