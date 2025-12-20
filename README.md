# Edu Cloud

一个模仿北京邮电大学（BUPT）Ucloud核心功能的多用户Web应用程序，旨在简化学生访问校内系统的流程。

## 🎯 项目目标

构建一个完整的多用户在线系统，复现Ucloud的关键功能，为北京邮电大学学生提供更好的校园系统访问体验。

## 🚀 核心功能

### 基本功能
- **用户系统**: 支持多用户注册、登录和个人空间，实现数据隔离
  - 本地账号注册和登录
  - CAS统一认证登录（支持北京邮电大学CAS系统）
  - JWT令牌认证和会话管理
  - 用户角色管理（普通用户/管理员）
- **课程管理**: 完整的课程信息管理
  - 课程列表展示和详情查看
  - 课程信息同步（从学校系统抓取）
  - 本学期课程筛选
- **作业管理**: 全面的作业功能
  - 作业列表展示（支持筛选和排序）
  - 作业详情查看
  - 作业同步（从学校系统自动抓取）
  - 作业提交（支持文件上传）
- **讨论区**: 课程讨论和交流
  - 讨论主题发布和回复
  - 讨论内容管理
- **通知系统**: 消息和通知管理
  - 系统通知推送
  - 通知列表和详情查看
- **管理员功能**: 系统管理后台
  - 用户管理（查看、编辑、删除）
  - 系统数据管理
  - 权限控制

### 用户界面
- **PyQt6桌面应用**: 基于Fluent Widgets的现代化GUI客户端
  - 美观的现代化界面设计
  - 完整的作业管理功能
  - 支持深色/浅色主题切换
- **PyWebIO Web界面**: 基于Web的轻量级界面
  - 课程大厅展示
  - 作业详情和提交
  - 响应式布局设计

### 技术特性
- **现代化架构**: 基于Flask构建的高性能Web应用
- **数据库支持**: SQLAlchemy ORM，支持SQLite/PostgreSQL
- **用户认证**: 安全的JWT用户认证和会话管理
- **API设计**: RESTful API设计，完整的错误处理
- **多端支持**: 同时支持Web API、桌面GUI和Web界面
- **数据同步**: 支持从学校系统自动同步课程和作业数据

## 🛠 技术栈

### 后端技术
- **语言**: Python 3.12+
- **框架**: Flask 3.0+
- **数据库**: SQLAlchemy ORM 2.0+
- **依赖管理**: pyproject.toml + uv
- **认证**: JWT令牌认证 (Flask-JWT-Extended)
- **CAS认证**: 支持北京邮电大学CAS统一认证
- **数据抓取**: buptmw库（学校系统数据同步）

### 前端技术
- **桌面GUI**: PyQt6 + PyQt6-Fluent-Widgets
  - 现代化Fluent Design风格界面
  - 支持深色/浅色主题
  - 完整的桌面应用体验
- **Web界面**: PyWebIO
  - 轻量级Web界面框架
  - 快速原型开发
  - 响应式布局
- **Web API**: RESTful API
  - 标准JSON格式
  - 完整的CORS支持
  - 详细的错误处理

## 📁 项目结构

```
edu_cloud/
├── src/
│   └── edu_cloud/
│       ├── __init__.py
│       ├── common/                 # 公共模块
│       │   ├── __init__.py
│       │   ├── auth.py           # 认证模块
│       │   ├── cas_auth.py        # CAS认证
│       │   ├── config.py          # 配置管理
│       │   ├── database.py        # 数据库连接
│       │   ├── security.py        # 安全相关
│       │   └── token_manager.py   # Token管理
│       ├── user/                  # 用户模块
│       │   ├── __init__.py
│       │   ├── api.py            # 用户API路由
│       │   ├── models.py         # 用户数据模型
│       │   ├── schemas.py        # 用户数据验证
│       │   └── tests.py         # 用户功能测试
│       ├── course/                # 课程模块
│       │   ├── __init__.py
│       │   ├── api.py            # 课程API路由
│       │   ├── models.py         # 课程数据模型
│       │   ├── scraper.py        # 课程数据抓取
│       │   └── services.py       # 课程业务逻辑
│       ├── assignment/            # 作业模块
│       │   ├── __init__.py
│       │   ├── api.py            # 作业API路由
│       │   ├── models.py         # 作业数据模型
│       │   ├── schemas.py        # 作业数据验证
│       │   ├── scraper.py        # 作业数据抓取
│       │   └── services.py       # 作业业务逻辑
│       ├── discussion/            # 讨论区模块
│       │   ├── __init__.py
│       │   ├── api.py            # 讨论API路由
│       │   ├── models.py         # 讨论数据模型
│       │   ├── scraper.py        # 讨论数据抓取
│       │   └── services.py       # 讨论业务逻辑
│       ├── notification/          # 通知模块
│       │   ├── __init__.py
│       │   ├── api.py            # 通知API路由
│       │   ├── models.py         # 通知数据模型
│       │   ├── scraper.py        # 通知数据抓取
│       │   └── services.py       # 通知业务逻辑
│       ├── admin/                 # 管理员模块
│       │   ├── __init__.py
│       │   ├── api.py            # 管理员API路由
│       │   └── ADMIN_README.md   # 管理员文档
│       └── scripts/               # 脚本模块
│           ├── __init__.py
│           ├── create_admin.py   # 创建管理员脚本
│           └── migrate_*.py     # 数据库迁移脚本
├── gui/                           # GUI桌面应用
│   ├── __init__.py
│   ├── main.py                   # GUI应用入口
│   ├── api_client.py             # API客户端
│   ├── config.py                 # GUI配置
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务服务
│   ├── utils/                    # 工具模块
│   └── views/                    # 界面视图
│       ├── login_window.py       # 登录窗口
│       ├── main_window.py        # 主窗口
│       ├── admin_window.py       # 管理员窗口
│       └── components/           # UI组件
├── main.py                       # Flask API入口
├── web_ui.py                     # PyWebIO Web界面
├── start_gui.py                  # GUI启动脚本
├── start_web.py                  # Web启动脚本
├── pyproject.toml                # 项目配置
├── config/                       # 配置文件目录
├── README.md                     # 项目文档
├── GUI_README.md                 # GUI使用说明
└── WEB_UI_README.md              # Web界面使用说明
```

## 🚀 快速开始

### 环境要求
- Python 3.12+
- uv (现代Python包管理工具)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/87361/Edu_Cloud.git
   cd edu_cloud
   ```

2. **安装依赖**
   ```bash
   uv sync
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件，设置必要的配置：
   ```env
   DATABASE_URL="sqlite:///./app.db"
   SECRET_KEY="your_secret_key_here"
   JWT_SECRET_KEY="your_jwt_secret_key_here"
   ```

4. **安装项目包**
   ```bash
   uv pip install -e .
   ```

5. **（可选）创建管理员账户**
   ```bash
   python -m src.edu_cloud.scripts.create_admin
   ```
   按照提示输入管理员用户名、邮箱和密码。

6. **启动应用**

   项目提供三种启动方式：

   **方式一：启动Flask API服务器**
   ```bash
   uv run python main.py
   ```
   - API根路径: http://localhost:5000
   - 健康检查: http://localhost:5000/health

   **方式二：启动GUI桌面应用**
   ```bash
   python start_gui.py
   ```
   或
   ```bash
   python -m gui.main
   ```
   - 需要先启动Flask API服务器
   - 支持本地账号和CAS登录
   - 详细使用说明请参考 [GUI_README.md](gui/GUI_README.md)

   **方式三：启动Web界面**
   ```bash
   # 终端1：启动Flask API
   uv run python main.py
   
   # 终端2：启动PyWebIO界面
   uv run python web_ui.py
   ```
   - Flask API: http://localhost:5000
   - Web界面: http://localhost:8080
   - 详细使用说明请参考 [WEB_UI_README.md](WEB_UI_README.md)

6. **访问应用**
   - API根路径: http://localhost:5000
   - Web界面: http://localhost:8080 (如果启动)
   - GUI应用: 运行启动脚本后自动打开窗口

## 📖 API文档

### 用户API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| POST | `/api/user/register` | 用户注册 | 无 |
| POST | `/api/user/login` | 用户登录（本地账号） | 无 |
| POST | `/api/user/cas-login` | CAS统一认证登录 | 无 |
| POST | `/api/user/token` | 获取JWT令牌 | 无 |
| GET | `/api/user/me` | 获取当前用户信息 | 需要 |
| PUT | `/api/user/me` | 更新用户信息 | 需要 |
| PATCH | `/api/user/me` | 部分更新用户信息 | 需要 |
| DELETE | `/api/user/me` | 删除用户账户 | 需要 |
| POST | `/api/user/change-password` | 修改密码 | 需要 |
| POST | `/api/user/logout` | 用户登出 | 需要 |
| GET | `/api/user/` | 获取用户列表 | 需要 |

### 课程API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| GET | `/api/course/` | 获取课程列表 | 需要 |
| GET | `/api/course/<id>` | 获取课程详情 | 需要 |
| GET | `/api/course/current-semester` | 获取本学期课程 | 需要 |
| POST | `/api/course/sync` | 同步课程数据 | 需要 |

### 作业API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| GET | `/api/assignment/` | 获取作业列表 | 需要 |
| GET | `/api/assignment/<id>` | 获取作业详情 | 需要 |
| POST | `/api/assignment/sync` | 同步作业数据 | 需要 |
| POST | `/api/assignment/<id>/submit` | 提交作业 | 需要 |

### 讨论区API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| GET | `/api/discussion/` | 获取讨论列表 | 需要 |
| GET | `/api/discussion/<id>` | 获取讨论详情 | 需要 |
| POST | `/api/discussion/` | 创建讨论 | 需要 |
| POST | `/api/discussion/<id>/reply` | 回复讨论 | 需要 |

### 通知API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| GET | `/api/notification/` | 获取通知列表 | 需要 |
| GET | `/api/notification/<id>` | 获取通知详情 | 需要 |
| POST | `/api/notification/sync` | 同步通知数据 | 需要 |

### 管理员API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| GET | `/api/admin/users` | 获取用户列表 | 管理员 |
| GET | `/api/admin/users/<id>` | 获取用户详情 | 管理员 |
| PUT | `/api/admin/users/<id>` | 更新用户信息 | 管理员 |
| DELETE | `/api/admin/users/<id>` | 删除用户 | 管理员 |

### 请求示例

```bash
# 用户注册
curl -X POST http://localhost:5000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# 用户登录
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# 获取用户信息 (需要认证)
curl -X GET http://localhost:5000/api/user/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 开发指南

### 运行测试

```bash
# 运行所有测试
uv run pytest src/edu_cloud/user/tests.py -v

# 运行特定测试
uv run pytest src/edu_cloud/user/tests.py::TestUserAPI::test_register_success -v
```

### 添加新模块

1. 在 `src/edu_cloud/` 下创建新模块目录
2. 创建必要的文件：`__init__.py`, `api.py`, `models.py`, `schemas.py`, `tests.py`
3. 在 `main.py` 中注册新的API路由

### 数据库操作

```python
# 创建数据库表
from src.edu_cloud.common.database import engine, Base
Base.metadata.create_all(bind=engine)

# 获取数据库会话
from src.edu_cloud.common.database import get_db
db = next(get_db())
```

### 添加新的API端点

```python
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from src.edu_cloud.common.database import get_db

blueprint = Blueprint('example', __name__, url_prefix='/api/example')

@blueprint.route("/example", methods=['GET'])
def get_example():
    db = next(get_db())
    # 数据库操作
    return jsonify({"message": "Example endpoint"})
```

## 🔐 安全考虑

- 使用环境变量管理敏感配置
- 实现了基于JWT的用户认证
- 数据库连接使用SQLAlchemy ORM防止SQL注入
- API端点适当的权限验证
- 输入验证和XSS防护

## 📋 测试覆盖

项目包含全面的测试套件，覆盖以下功能：

### 用户模块测试
- ✅ 用户注册和验证
- ✅ 用户登录和认证
- ✅ 个人信息管理
- ✅ 密码修改和安全性
- ✅ 用户权限和隔离
- ✅ 错误处理和边界情况

### 测试统计
- **总测试用例**: 13个
- **测试覆盖率**: 100%核心功能
- **测试框架**: pytest

运行测试：
```bash
uv run pytest src/edu_cloud/user/tests.py -v --tb=short
```

## 📝 开发原则

### 技术约束
1. **Python优先**: 所有核心功能使用Python实现
2. **前端验证**: 前端主要用于展示后端功能，UI追求快速实现
3. **模块化设计**: 清晰的模块分离和职责划分

### 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8代码风格
- 模块化设计，职责分离
- 完善的错误处理
- 全面的测试覆盖

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v2.0.0 (当前版本)
- ✅ **课程管理系统**：完整的课程信息管理功能
  - 课程列表和详情查看
  - 课程数据同步（从学校系统抓取）
  - 本学期课程筛选
- ✅ **作业管理系统**：全面的作业功能
  - 作业列表展示（支持筛选和排序）
  - 作业详情查看
  - 作业数据同步（从学校系统自动抓取）
  - 作业提交（支持文件上传）
- ✅ **讨论区功能**：课程讨论和交流
  - 讨论主题发布和回复
  - 讨论内容管理
- ✅ **通知系统**：消息和通知管理
  - 系统通知推送
  - 通知列表和详情查看
- ✅ **管理员功能**：系统管理后台
  - 用户管理（查看、编辑、删除）
  - 系统数据管理
  - 权限控制
- ✅ **CAS认证支持**：统一认证登录
  - 支持北京邮电大学CAS系统
  - 自动获取用户信息
- ✅ **PyQt6桌面应用**：现代化GUI客户端
  - 基于Fluent Widgets的美观界面
  - 完整的作业管理功能
  - 支持深色/浅色主题切换
  - 管理员和普通用户界面分离
- ✅ **PyWebIO Web界面**：轻量级Web界面
  - 课程大厅展示
  - 作业详情和提交
  - 响应式布局设计
- ✅ **数据同步功能**：自动同步学校系统数据
  - 课程信息同步
  - 作业信息同步
  - 通知信息同步
- ✅ **多端支持**：同时支持Web API、桌面GUI和Web界面
- ✅ **性能优化**：异步处理和缓存优化

### v1.0.0
- ✅ 项目初始化和Flask迁移
- ✅ 用户认证系统完整实现
- ✅ 数据库配置和模型
- ✅ Flask应用框架搭建
- ✅ 用户API端点完整实现
- ✅ JWT认证和安全防护
- ✅ 全面的测试套件
- ✅ 错误处理和验证

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/87361/Edu_Cloud/issues)
- 邮箱: 1316757358@qq.com

---

