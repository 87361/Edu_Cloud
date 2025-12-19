# 管理员功能使用说明

## 概述

本系统已添加管理员身份账号和数据库查看功能。管理员可以查看数据库表结构、数据统计、用户列表等信息。

## 功能特性

1. **管理员角色**：用户角色分为 `user`（普通用户）和 `admin`（管理员）
2. **权限控制**：管理员API端点需要管理员权限才能访问
3. **数据库查看**：管理员可以查看数据库表、数据统计、表数据等

## 快速开始

### 1. 数据库迁移（如果已有数据）

如果数据库中已有用户数据，需要先运行迁移脚本添加 `role` 字段：

```bash
python -m src.edu_cloud.scripts.migrate_add_role_field
```

### 2. 创建管理员账号

有两种方式创建管理员账号：

#### 方式一：使用脚本（推荐）

```bash
# 交互式创建
python -m src.edu_cloud.scripts.create_admin

# 命令行参数创建
python -m src.edu_cloud.scripts.create_admin <username> <password> [email]
```

示例：
```bash
python -m src.edu_cloud.scripts.create_admin admin admin123 admin@example.com
```

#### 方式二：将现有用户升级为管理员

运行脚本时，如果用户名已存在，会提示是否将现有用户升级为管理员。

### 3. 登录获取Token

使用管理员账号登录获取访问令牌：

```bash
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

响应示例：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## API端点

所有管理员API端点都需要在请求头中包含JWT token：

```
Authorization: Bearer <access_token>
```

### 1. 获取数据库表列表

查看所有数据库表及其结构：

```bash
GET /api/admin/database/tables
```

响应示例：
```json
{
  "data": {
    "tables": [
      {
        "name": "users",
        "columns": [
          {
            "name": "id",
            "type": "INTEGER",
            "nullable": false
          },
          ...
        ],
        "column_count": 10
      }
    ],
    "table_count": 2
  }
}
```

### 2. 获取数据库统计信息

查看用户、token等统计信息：

```bash
GET /api/admin/database/stats
```

响应示例：
```json
{
  "data": {
    "users": {
      "total": 100,
      "active": 95,
      "inactive": 5,
      "admins": 2,
      "cas_bound": 50
    },
    "tokens": {
      "total_revoked": 20,
      "active_revoked": 5,
      "expired_revoked": 15
    },
    "database": {
      "size_bytes": 1048576,
      "size_mb": 1.0
    }
  }
}
```

### 3. 查看表数据

查看指定表的数据（支持分页）：

```bash
GET /api/admin/database/table/<table_name>?limit=100&offset=0
```

参数：
- `limit`: 返回记录数（默认100，最大1000）
- `offset`: 偏移量（默认0）

示例：
```bash
GET /api/admin/database/table/users?limit=50&offset=0
```

响应示例：
```json
{
  "data": {
    "table_name": "users",
    "data": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        ...
      }
    ],
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### 4. 获取所有用户列表

查看所有用户（支持筛选和分页）：

```bash
GET /api/admin/users?limit=100&offset=0&role=user&is_active=true
```

参数：
- `limit`: 返回记录数（默认100）
- `offset`: 偏移量（默认0）
- `role`: 按角色筛选（可选：'user' 或 'admin'）
- `is_active`: 按活跃状态筛选（可选：'true' 或 'false'）

### 5. 查看Token黑名单

查看已撤销的token列表：

```bash
GET /api/admin/tokens/blacklist?limit=100&offset=0&username=admin
```

参数：
- `limit`: 返回记录数（默认100）
- `offset`: 偏移量（默认0）
- `username`: 按用户名筛选（可选）

### 6. 管理员健康检查

验证管理员权限：

```bash
GET /api/admin/health
```

## 权限说明

- **普通用户（role='user'）**：
  - 可以访问 `/api/user/*` 下的用户相关API
  - 无法访问管理员API

- **管理员（role='admin'）**：
  - 可以访问所有用户API
  - 可以访问 `/api/admin/*` 下的所有管理员API
  - 可以查看数据库信息、用户列表等

## 安全注意事项

1. **管理员账号安全**：
   - 使用强密码
   - 定期更换密码
   - 不要将管理员账号信息泄露

2. **Token安全**：
   - Token有过期时间（默认30分钟）
   - 登出时token会被撤销
   - 不要在公共场合暴露token

3. **数据库查看**：
   - 管理员可以查看所有数据，包括敏感信息
   - 生产环境应限制管理员账号数量
   - 建议记录管理员操作日志

## 故障排除

### 问题：无法访问管理员API

1. 检查token是否有效（未过期、未撤销）
2. 确认用户角色是否为 `admin`
3. 检查请求头是否正确：`Authorization: Bearer <token>`

### 问题：迁移脚本失败

1. 确保数据库文件存在且有写权限
2. 检查是否有其他进程正在使用数据库
3. 查看错误信息，可能需要手动修复

### 问题：创建管理员失败

1. 检查用户名是否已存在
2. 确认密码长度至少6个字符
3. 检查数据库连接是否正常

## 示例代码

### Python示例

```python
import requests

# 登录获取token
login_response = requests.post(
    'http://localhost:5000/api/user/login',
    json={'username': 'admin', 'password': 'admin123'}
)
token = login_response.json()['access_token']

# 设置请求头
headers = {'Authorization': f'Bearer {token}'}

# 获取数据库统计
stats_response = requests.get(
    'http://localhost:5000/api/admin/database/stats',
    headers=headers
)
print(stats_response.json())

# 获取用户列表
users_response = requests.get(
    'http://localhost:5000/api/admin/users',
    headers=headers,
    params={'limit': 10, 'role': 'user'}
)
print(users_response.json())
```

### cURL示例

```bash
# 登录
TOKEN=$(curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 获取数据库统计
curl -X GET http://localhost:5000/api/admin/database/stats \
  -H "Authorization: Bearer $TOKEN"

# 获取用户列表
curl -X GET "http://localhost:5000/api/admin/users?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 更新日志

- **v1.0.0** (2025.12.19): 初始版本
  - 添加管理员角色支持
  - 实现数据库查看功能
  - 添加权限控制装饰器

