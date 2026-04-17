# 部署遇到的 Issues 及解决方案

> 本文档记录了在华为云 openEuler 服务器上部署 **FastAPI + OpenGauss** 项目时遇到的所有问题，包含详细的背景知识和解决思路，适合学习参考。

---

## Issue 1：系统默认 Python 被替换后 dnf/yum 无法使用

### 现象

执行 `dnf` 或 `yum` 命令时报错，无法安装任何软件包。

### 背景知识

openEuler（及 CentOS 8+、RHEL 8+）系统中，`dnf` 和 `yum` 是用 **Python 3** 编写的包管理器。系统默认的 `/usr/bin/python` 是一个**软链接**，通常指向 `python2`。系统中同时存在 Python 2 和 Python 3，各有用途：

```
/usr/bin/python  → python2（系统默认，部分旧脚本依赖）
/usr/bin/python2 → python2.7
/usr/bin/python3 → python3.7
```

### 根因

之前为了方便使用 Python 3，执行了以下操作：

```bash
cd /usr/bin
mv python python.bak          # 备份原来的 python 软链接
ln -s python3 /usr/bin/python  # 让 python 指向 python3
```

这导致依赖 `python` 命令的系统脚本行为异常。虽然 `dnf` 本身用的是 `python3`，但系统中还有很多脚本（如 `dnf` 的依赖模块路径解析）依赖原始的软链接关系。

### 解决方法

恢复原始的软链接：

```bash
rm -f /usr/bin/python                  # 删除指向 python3 的错误软链接
mv /usr/bin/python.bak /usr/bin/python # 还原备份
python -V                              # 验证：应输出 Python 2.7.x
```

### 最佳实践

永远不要修改 `/usr/bin/python` 的指向。如果想方便地使用 Python 3，有以下安全的替代方式：

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

## Issue 2：dnf 报错 `ImportError: libcurl.so.4: symbol SSLv3_client_method`

### 现象

运行 `dnf` 时出现如下错误：

```
ImportError: /lib64/libcurl.so.4: symbol SSLv3_client_method version OPENSSL_1_1_0
not defined in file libssl.so.1.1 with link time reference
...
ModuleNotFoundError: No module named '_common_types'
```

### 背景知识

Linux 程序运行时需要加载**动态链接库**（`.so` 文件，类似 Windows 的 `.dll`）。系统通过以下顺序查找 `.so` 文件：

1. **`LD_LIBRARY_PATH`** 环境变量指定的目录（**最高优先级**）
2. `/etc/ld.so.cache` 缓存（由 `ldconfig` 生成）
3. 默认路径 `/lib64`、`/usr/lib64`

`libcurl`（HTTP 客户端库）依赖 `libssl`（OpenSSL 加密库）。如果加载了**错误版本**的 `libssl`，就会因为缺少符号（函数）而报错。

### 根因

openGauss 安装时在 `/etc/profile` 中添加了一行：

```bash
export LD_LIBRARY_PATH=/opt/software/openGauss/script/gspylib/clib:$LD_LIBRARY_PATH
```

这使得**所有程序**优先加载 openGauss 自带的 `libssl.so.1.1`（位于 `/opt/software/openGauss/script/gspylib/clib/`），而不是系统的 `/lib64/libssl.so.1.1`。openGauss 自带的 OpenSSL 版本移除了 `SSLv3_client_method` 这个已废弃的函数，导致 `libcurl` 找不到它需要的符号。

### 排查过程

用 `ldd` 命令验证（`ldd` 显示程序实际加载的动态库路径）：

```bash
# 查看 libcurl 实际加载的 libssl 来自哪里
ldd /lib64/libcurl.so.4 | grep ssl
# 输出：libssl.so.1.1 => /opt/software/openGauss/script/gspylib/clib/libssl.so.1.1
# ↑ 加载了 openGauss 的版本，而不是系统的 /lib64/libssl.so.1.1

# 查看系统的 libssl 是否有该符号
nm -D /lib64/libssl.so.1.1 | grep SSLv3_client_method
# 输出：00000000000212e8 T SSLv3_client_method  ← 系统版本有这个符号

# 查看当前 LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH
# 输出：/opt/software/openGauss/script/gspylib/clib:

# 查看是谁设置的
grep 'LD_LIBRARY_PATH' /etc/profile
# 输出：export LD_LIBRARY_PATH=$packagePath/script/gspylib/clib:$LD_LIBRARY_PATH
```

### 解决方法

运行 `dnf` 时临时清除 `LD_LIBRARY_PATH`，让它使用系统默认的库：

```bash
# 在命令前加 LD_LIBRARY_PATH="" 临时覆盖环境变量
LD_LIBRARY_PATH="" dnf install <包名> -y

# 示例
LD_LIBRARY_PATH="" dnf install git --nogpgcheck -y
LD_LIBRARY_PATH="" dnf clean packages
```

### 知识点

`VAR=value command` 是 bash 语法，表示**仅在执行 `command` 时**临时设置环境变量 `VAR`，不影响当前 shell。例如：

```bash
LD_LIBRARY_PATH="" dnf install git -y   # 仅 dnf 执行时 LD_LIBRARY_PATH 为空
echo $LD_LIBRARY_PATH                    # 当前 shell 中仍然是原来的值
```

---

## Issue 3：dnf 安装包时报 `GPG check FAILED`

### 现象

```
Package perl-TermReadKey-2.38-2.oe1.aarch64.rpm is not signed
Error: GPG check FAILED
```

### 背景知识

Linux 包管理器默认会对下载的 `.rpm` 包进行 **GPG 签名验证**，确保包来自可信的发布者且未被篡改。这是一种安全机制：

```
发布者 → 用私钥对 .rpm 包签名 → 上传到仓库
用户   → 下载 .rpm 包 → 用公钥验证签名 → 确认包未被篡改
```

如果某个包没有签名（`is not signed`），验证就会失败。

### 根因

openEuler 的 `update` 仓库中，部分包（如 `perl-TermReadKey`）没有 GPG 签名。

### 解决方法

安装时加 `--nogpgcheck` 参数跳过签名验证：

```bash
LD_LIBRARY_PATH="" dnf install git --nogpgcheck -y
```

> **安全提示：** 跳过 GPG 检查意味着不验证包的来源和完整性，仅在可信的仓库源上使用。生产环境应尽量保持 GPG 检查开启。

---

## Issue 4：pip 安装依赖超时

### 现象

执行 `pip3 install -r requirement.txt` 时报错：

```
pip._vendor.urllib3.exceptions.ReadTimeoutError:
  HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

### 背景知识

`pip` 默认从 **PyPI**（Python Package Index，`https://pypi.org`）下载包，其服务器在国外。从国内服务器访问速度很慢，经常超时。

国内有很多高校和企业维护了 PyPI 的**镜像源**（完整复制），定期同步，可以大幅提升下载速度：

| 镜像源 | 地址 |
|--------|------|
| 清华大学（推荐） | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple/` |
| 豆瓣 | `https://pypi.douban.com/simple/` |

### 解决方法

**临时使用镜像源：**

```bash
pip3 install -r requirement.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn
```

- `-i`：指定镜像源 URL
- `--trusted-host`：信任该主机（跳过 SSL 证书验证）

**永久设置镜像源（推荐）：**

```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

设置后，以后执行 `pip3 install` 会自动使用清华源，不用每次加 `-i` 参数。

---

## Issue 5：`psql` 包名找不到

### 现象

```bash
dnf install psql
# Error: Unable to find a match: psql
```

### 根因

`psql` 是 PostgreSQL 的**命令行客户端工具**，但它不是一个独立的包。它包含在 `postgresql` 包中。

### 解决方法

```bash
LD_LIBRARY_PATH="" dnf install postgresql --nogpgcheck -y
```

### 知识点

在 Linux 中，如果不确定某个命令属于哪个包，可以用以下方法查找：

```bash
# 方法 1：用 dnf provides 查找命令属于哪个包
dnf provides '*/psql'
# 输出：postgresql-10.5-20.oe1.aarch64 : PostgreSQL client programs

# 方法 2：如果命令已安装，用 rpm -qf 查看
rpm -qf $(which psql)
# 输出：postgresql-10.5-20.oe1.aarch64
```

---

## Issue 6：OpenGauss 数据库启动失败（内存不足）

### 现象

以 `omm` 用户执行 `gs_om -t start` 时报错：

```
FATAL:  could not create shared memory segment: Cannot allocate memory
DETAIL: Failed system call was shmget(key=26000001, size=1993433088, 03600).
```

### 背景知识

OpenGauss（基于 PostgreSQL）启动时需要分配一块**共享内存（Shared Memory）**，用于多个进程之间共享数据：

```
┌───────────────────────────────────────────┐
│           操作系统物理内存 (2.8GB)          │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │     OpenGauss 共享内存 (1.9GB!!)     │  │ ← shmget() 申请
│  │  ┌───────────┐  ┌───────────────┐   │  │
│  │  │shared_buf │  │  WAL buffers  │   │  │
│  │  │  256MB    │  │    320MB      │   │  │
│  │  └───────────┘  └───────────────┘   │  │
│  │  ┌───────────────────────────────┐  │  │
│  │  │  连接管理 (5000连接 × 内存)    │  │  │
│  │  └───────────────────────────────┘  │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  ┌──────────┐  ┌──────────┐               │
│  │ 操作系统  │  │ 其他进程  │               │
│  └──────────┘  └──────────┘               │
└───────────────────────────────────────────┘
```

数据库根据 `postgresql.conf` 中的参数计算所需的共享内存大小。如果计算出的大小超过操作系统可用的内存，`shmget()` 系统调用就会失败。

### 根因

服务器只有 **2.8GB 内存**（`free -h` 查看），但数据库配置文件中的参数是按大内存服务器设置的。

### 排查过程

```bash
# 1. 查看系统内存
free -h
# total: 2.8Gi, used: 1.1Gi, free: 399Mi

# 2. 查看数据库内存配置
grep -E 'max_process_memory|shared_buffers|max_connections|work_mem|maintenance_work_mem' \
  /gaussdb/data/db1/postgresql.conf
```

### 解决方法

编辑 `/gaussdb/data/db1/postgresql.conf`，降低内存相关参数：

```bash
sed -i 's/^max_process_memory = 4GB/max_process_memory = 2GB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^shared_buffers = 256MB/shared_buffers = 128MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^bulk_write_ring_size = 256MB/bulk_write_ring_size = 128MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^max_connections = 5000/max_connections = 200/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^work_mem = 64MB/work_mem = 8MB/' /gaussdb/data/db1/postgresql.conf
sed -i 's/^maintenance_work_mem = 128MB/maintenance_work_mem = 32MB/' /gaussdb/data/db1/postgresql.conf
```

修改对照表：

| 参数 | 原值 | 新值 | 含义 |
|------|------|------|------|
| `max_process_memory` | 4GB | **2GB** | 数据库进程最大可用内存总量，不超过物理内存 70% |
| `shared_buffers` | 256MB | **128MB** | 数据页缓存，通常设为内存的 15%-25% |
| `bulk_write_ring_size` | 256MB | **128MB** | 批量写入缓冲区，不超过 shared_buffers |
| `max_connections` | 5000 | **200** | 最大并发连接数，每个连接消耗内存，学习环境 200 足够 |
| `work_mem` | 64MB | **8MB** | 每个查询操作（排序、哈希）可用内存 |
| `maintenance_work_mem` | 128MB | **32MB** | 维护操作（VACUUM、CREATE INDEX）内存 |

修改后重启：

```bash
su - omm -c "gs_om -t start"
```

### 经验法则

- `max_process_memory` 不超过物理内存的 **60%-70%**
- `shared_buffers` 通常为物理内存的 **15%-25%**
- `max_connections` 根据实际并发需求设置，不要盲目设大
- 修改配置后需要**重启数据库**才能生效（端口、内存等参数）

---

## Issue 7：Git 克隆私有仓库报 `Permission denied (publickey)`

### 现象

```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

### 背景知识

GitHub 支持两种远程仓库访问方式：

| 方式 | URL 格式 | 认证方式 | 适用场景 |
|------|----------|----------|----------|
| SSH | `git@github.com:user/repo.git` | SSH 密钥对 | 频繁推送，免密码 |
| HTTPS | `https://github.com/user/repo.git` | 用户名 + Token | 临时使用，简单配置 |

SSH 认证流程：

```
1. 本机生成密钥对：私钥(id_ed25519) + 公钥(id_ed25519.pub)
2. 将公钥上传到 GitHub Settings → SSH Keys
3. git clone 时，GitHub 用你的公钥验证私钥签名
4. 验证通过 → 允许访问
```

### 根因

这台服务器是新机器，没有生成 SSH 密钥，也没有在 GitHub 上配置公钥。

### 解决方法

```bash
# 1. 生成 SSH 密钥对（-N "" 表示不设密码）
ssh-keygen -t ed25519 -C "github" -f ~/.ssh/id_ed25519 -N ""

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub
# 输出：ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... github

# 3. 将公钥添加到 GitHub
#    打开 https://github.com/settings/keys
#    点击 "New SSH key" → 粘贴公钥 → 保存

# 4. 测试连接
ssh -T git@github.com
# 成功输出：Hi username! You've been authenticated...

# 5. 克隆仓库
git clone git@github.com:123kaze/UserBack.git
```

### 知识点

- **私钥**（`id_ed25519`）：绝对不能泄露，相当于你的"密码"
- **公钥**（`id_ed25519.pub`）：可以公开分享，放到 GitHub 上
- **ed25519**：目前推荐的密钥算法，比 RSA 更安全且密钥更短
- 每台机器都需要生成自己的密钥对并在 GitHub 上配置

---

## Issue 8：修改 OpenGauss 数据库端口（26000 → 5432）

### 背景

OpenGauss 默认端口是 `26000`，而 PostgreSQL 标准端口是 `5432`。项目的 `database.py` 中连接字符串使用的是 `5432`，需要统一。

### 操作步骤

```bash
# 1. 停止数据库
su - omm -c "gs_om -t stop"

# 2. 修改 postgresql.conf 中的端口
sed -i 's/^port = 26000/port = 5432/' /gaussdb/data/db1/postgresql.conf

# 3. 修改集群配置文件中的端口
sed -i 's/26000/5432/g' /opt/software/openGauss/clusterconfig.xml

# 4. 启动数据库
su - omm -c "gs_om -t start"

# 5. 验证端口
ss -tlnp | grep 5432
```

---

## Issue 9：FastAPI 连接数据库报 `Connection refused`

### 现象

启动 uvicorn 后报错：

```
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432
failed: Connection refused
```

### 背景知识

数据库服务器通过 `listen_addresses` 参数控制**监听哪些 IP 地址**的连接：

```
listen_addresses = '192.168.0.60'   → 只接受来自 192.168.0.60 的连接
listen_addresses = 'localhost'      → 只接受来自 127.0.0.1 的连接
listen_addresses = '*'              → 接受所有 IP 的连接
```

### 排查过程

```bash
# 查看数据库监听了哪些地址
grep '^listen_addresses' /gaussdb/data/db1/postgresql.conf
# 输出：listen_addresses = '192.168.0.60'  ← 只监听了内网 IP，没有 localhost！

# 用 ss 命令确认（ss 显示当前网络连接状态）
ss -tlnp | grep 5432
# 只有 192.168.0.60:5432，没有 127.0.0.1:5432
```

### 根因

`listen_addresses` 只配置了服务器的内网 IP `192.168.0.60`，没有包含 `localhost`（`127.0.0.1`）。而 FastAPI 的连接字符串用的是 `localhost`。

### 解决方法

```bash
# 添加 localhost 到监听地址
sed -i "s/^listen_addresses = '192.168.0.60'/listen_addresses = 'localhost,192.168.0.60'/" \
  /gaussdb/data/db1/postgresql.conf

# 重启数据库
su - omm -c "gs_om -t restart"

# 验证：应同时看到 127.0.0.1:5432 和 192.168.0.60:5432
ss -tlnp | grep 5432
```

---

## Issue 10：连接数据库报 `Forbid remote connection with trust method!`

### 现象

```
FATAL: Forbid remote connection with trust method!
```

### 背景知识

数据库通过 `pg_hba.conf`（Host-Based Authentication，基于主机的认证配置）控制**谁能连、用什么方式认证**：

```
# 类型    数据库  用户  地址            认证方式
local     all     all                   trust      ← Unix socket 连接，免密码
host      all     all   127.0.0.1/32    trust      ← TCP 连接，免密码
host      all     all   ::1/128         trust      ← IPv6 本地连接，免密码
```

常见认证方式：

| 方式 | 说明 |
|------|------|
| `trust` | 完全信任，不需要密码（不安全） |
| `md5` | 用 MD5 哈希验证密码（PostgreSQL 标准） |
| `sha256` | 用 SHA-256 验证密码（openGauss 特有） |
| `reject` | 拒绝连接 |

### 根因

openGauss 出于安全考虑，**禁止 TCP 连接（`host` 类型）使用 `trust` 认证**。`trust` 意味着任何人只要能连到这个端口就能登录，非常不安全。

### 解决方法

将 `pg_hba.conf` 中 TCP 连接的认证方式从 `trust` 改为 `sha256`：

```bash
# 编辑 pg_hba.conf
vi /gaussdb/data/db1/pg_hba.conf

# 将 host 行的 trust 改为 sha256
host    all    all    127.0.0.1/32    sha256
host    all    all    ::1/128         sha256

# 重启数据库
su - omm -c "gs_om -t restart"
```

---

## Issue 11：连接数据库报 `none of the server's SASL authentication mechanisms are supported`

### 现象

```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432
failed: none of the server's SASL authentication mechanisms are supported
```

### 背景知识

这个问题涉及**认证协议的兼容性**：

```
客户端 (psycopg2)              服务端 (openGauss)
      │                              │
      │ ← 告知支持的认证方式 ──────── │  sha256 (openGauss 特有)
      │                              │
      │   psycopg2 支持:             │
      │   ✅ md5                     │
      │   ✅ scram-sha-256 (PG标准)  │
      │   ❌ sha256 (不认识!)        │
      │                              │
      │ ── 报错：不支持 ───────────► │
```

`psycopg2` 是标准的 PostgreSQL 驱动，只支持 PostgreSQL 标准的认证方式（`md5`、`scram-sha-256`）。openGauss 的 `sha256` 是它自己的认证协议，`psycopg2` 不认识。

### 根因

`pg_hba.conf` 中使用了 `sha256` 认证，`psycopg2` 不支持。

同时，openGauss 的 `password_encryption_type` 参数控制密码的**存储格式**：

| 值 | 含义 |
|----|------|
| 0 | 仅 md5 |
| 1 | sha256 + md5（兼容模式） |
| 2 | 仅 sha256（默认） |

如果设为 `2`，即使 `pg_hba.conf` 改为 `md5`，密码也不是 md5 格式存储的，认证仍会失败。

### 解决方法

**第一步：修改密码存储格式为兼容模式**

```bash
# 在 postgresql.conf 中启用 md5 兼容
sed -i 's/^#password_encryption_type = 2/password_encryption_type = 1/' \
  /gaussdb/data/db1/postgresql.conf
```

**第二步：修改 pg_hba.conf 认证方式为 md5**

```bash
# 将 sha256 改为 md5
sed -i 's|sha256|md5|g' /gaussdb/data/db1/pg_hba.conf
```

**第三步：重启数据库**

```bash
su - omm -c "gs_om -t restart"
```

**第四步：重新设置用户密码（重要！）**

因为改了密码加密方式，需要重新设置密码才能生成 md5 格式的哈希：

```bash
su - omm -c "gsql -d postgres -p 5432 -c \"ALTER USER kaze WITH PASSWORD '新密码';\""
```

> **注意：** openGauss 有密码重用限制，不能设置与最近使用过的密码相同的密码。

### 最终的 pg_hba.conf 配置

```
local   all    all                   trust     # Unix socket 本地连接免密（omm 管理用）
host    all    all    127.0.0.1/32   md5       # TCP IPv4 本地连接用 md5 认证
host    all    all    ::1/128        md5       # TCP IPv6 本地连接用 md5 认证
host    all    all    192.168.0.60/32 trust    # 内网 IP 连接
```

---

## Issue 12：创建表时报 `permission denied for schema public`

### 现象

FastAPI 启动时自动建表（`Base.metadata.create_all`），报错：

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.InsufficientPrivilege)
permission denied for schema public
```

### 背景知识

PostgreSQL / openGauss 中的**权限层次**：

```
服务器
└── 数据库 (employee_db)
    └── Schema (public)          ← 需要 CREATE 权限才能建表
        ├── 表 (departments)     ← 需要 INSERT/SELECT/UPDATE/DELETE 权限
        ├── 表 (positions)
        └── 表 (employees)
```

即使用户是数据库的 **OWNER**，也不一定有在 `public` schema 中建表的权限（取决于数据库版本和配置）。

### 根因

`kaze` 用户虽然是 `employee_db` 的所有者，但没有被授予在 `public` schema 中创建对象的权限。

### 解决方法

```bash
su - omm -c "gsql -d employee_db -p 5432 -c \
  \"GRANT ALL PRIVILEGES ON SCHEMA public TO kaze; \
   GRANT ALL ON ALL TABLES IN SCHEMA public TO kaze;\""
```

- `GRANT ALL PRIVILEGES ON SCHEMA public TO kaze`：授予在 public schema 中创建/使用对象的权限
- `GRANT ALL ON ALL TABLES IN SCHEMA public TO kaze`：授予对已有表的所有操作权限

---

## Issue 13：Python 3.7 不支持 `list[...]` 类型注解语法

### 现象

```
TypeError: 'type' object is not subscriptable
```

出错代码：

```python
@router.get("/", response_model=list[schemas.DepartmentResponse])
```

### 背景知识

Python 的**类型注解**语法在不同版本中有差异：

| 语法 | 支持版本 | 说明 |
|------|----------|------|
| `list[int]` | Python 3.9+ | 内置类型直接下标 |
| `List[int]` | Python 3.5+ | 需要 `from typing import List` |
| `dict[str, int]` | Python 3.9+ | 内置类型直接下标 |
| `Dict[str, int]` | Python 3.5+ | 需要 `from typing import Dict` |

### 根因

服务器的 Python 版本是 **3.7**，不支持 `list[...]` 语法（这是 Python 3.9 才引入的）。

### 解决方法

将 `list[...]` 改为 `List[...]`，并导入 `typing`：

```python
from typing import List

@router.get("/", response_model=List[schemas.DepartmentResponse])
```

---

## Issue 总结：创建数据库用户的完整流程

综合以上所有 Issue，在 openGauss 中为 FastAPI 项目创建可用的数据库用户的完整步骤：

```bash
# 1. 修改密码加密方式为兼容模式（支持 md5）
sed -i 's/^#password_encryption_type = 2/password_encryption_type = 1/' \
  /gaussdb/data/db1/postgresql.conf

# 2. 修改 pg_hba.conf，TCP 连接用 md5 认证
# host  all  all  127.0.0.1/32  md5
# host  all  all  ::1/128       md5

# 3. 修改 listen_addresses 包含 localhost
# listen_addresses = 'localhost,192.168.0.60'

# 4. 重启数据库
su - omm -c "gs_om -t restart"

# 5. 创建用户
su - omm -c "gsql -d postgres -p 5432 -c \"CREATE USER kaze WITH PASSWORD 'Kaze@654321';\""

# 6. 创建数据库
su - omm -c "gsql -d postgres -p 5432 -c \"CREATE DATABASE employee_db OWNER kaze;\""

# 7. 授予权限
su - omm -c "gsql -d employee_db -p 5432 -c \
  \"GRANT ALL PRIVILEGES ON DATABASE employee_db TO kaze;
   GRANT ALL PRIVILEGES ON SCHEMA public TO kaze;\""

# 8. 验证连接
su - omm -c "gsql -d employee_db -U kaze -h 127.0.0.1 -p 5432 -W 'Kaze@654321' \
  -c 'SELECT current_database(), current_user;'"
```

### FastAPI 连接字符串格式

```python
# 格式：postgresql+psycopg2://用户名:密码@主机:端口/数据库名
# 注意：密码中的 @ 符号需要 URL 编码为 %40
DATABASE_URL = "postgresql+psycopg2://kaze:Kaze%40654321@localhost:5432/employee_db"
```
