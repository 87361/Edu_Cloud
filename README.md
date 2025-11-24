# Edu Cloud

一个模仿北京邮电大学（BUPT）Ucloud核心功能的多用户Web应用程序，旨在简化学生访问校内系统的流程。

## 🎯 项目目标

构建一个完整的多用户在线系统，复现Ucloud的关键功能，为北京邮电大学学生提供更好的校园系统访问体验。

## 🚀 核心功能

### 基本功能
- **用户系统**: 支持多用户注册、登录和个人空间，实现数据隔离
- **个人主页**: 展示用户的个人信息、本学期课程列表、待办事项和消息
- **课程详情页**: 包含课程基本信息、讲义/主页、作业列表与详情、讨论区、公告栏

### 技术特性
- **现代化架构**: 基于Flask构建的高性能Web应用
- **数据库支持**: SQLAlchemy ORM，支持SQLite/PostgreSQL
- **用户认证**: 安全的JWT用户认证和会话管理
- **API设计**: RESTful API设计，完整的错误处理

## 🛠 技术栈

### 后端技术
- **语言**: Python 3.12+
- **框架**: Flask
- **数据库**: SQLAlchemy ORM
- **依赖管理**: pyproject.toml + uv
- **认证**: JWT令牌认证

### 前端技术
- **框架**: Vue.js (次要验证性功能)
- **构建工具**: Vite

## 📁 项目结构

```
edu_cloud/
├── src/
│   └── edu_cloud/
│       ├── __init__.py
│       ├── common/                 # 公共模块
│       │   ├── __init__.py
│       │   ├── auth.py           # 认证模块
│       │   ├── config.py          # 配置管理
│       │   ├── database.py        # 数据库连接
│       │   └── security.py        # 安全相关
│       ├── user/                  # 用户模块
│       │   ├── __init__.py
│       │   ├── api.py            # 用户API路由
│       │   ├── models.py         # 用户数据模型
│       │   ├── schemas.py        # 用户数据验证
│       │   └── tests.py         # 用户功能测试
│       ├── course/                # 课程模块
│       │   ├── __init__.py
│       │   ├── api.py
│       │   ├── models.py
│       │   └── schemas.py
│       ├── assignment/            # 作业模块
│       │   ├── __init__.py
│       │   ├── api.py
│       │   ├── models.py
│       │   └── schemas.py
│       └── scripts/               # 脚本模块
│           └── __init__.py
├── main.py                        # 应用入口
├── pyproject.toml                # 项目配置
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── TEST_REPORT.md                # 测试报告
├── FINAL_TEST_REPORT.md          # 完整测试报告
└── README.md                     # 项目文档
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

5. **启动应用**
   ```bash
   uv run python main.py
   ```

6. **访问应用**
   - API根路径: http://localhost:5000
   - 用户API: http://localhost:5000/api/user

## 📖 API文档

### 用户API端点

| 方法 | 端点 | 功能 | 认证 |
|------|--------|------|--------|
| POST | `/api/user/register` | 用户注册 | 无 |
| POST | `/api/user/login` | 用户登录 | 无 |
| POST | `/api/user/token` | 获取JWT令牌 | 无 |
| GET | `/api/user/me` | 获取当前用户信息 | 需要 |
| PUT | `/api/user/me` | 更新用户信息 | 需要 |
| PATCH | `/api/user/me` | 部分更新用户信息 | 需要 |
| DELETE | `/api/user/me` | 删除用户账户 | 需要 |
| POST | `/api/user/change-password` | 修改密码 | 需要 |
| POST | `/api/user/logout` | 用户登出 | 需要 |
| GET | `/api/user/` | 获取用户列表 | 需要 |

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

### v1.0.0 (当前版本)
- ✅ 项目初始化和Flask迁移
- ✅ 用户认证系统完整实现
- ✅ 数据库配置和模型
- ✅ Flask应用框架搭建
- ✅ 用户API端点完整实现
- ✅ JWT认证和安全防护
- ✅ 全面的测试套件
- ✅ 错误处理和验证

### 计划功能
- 🔄 课程管理系统
- 🔄 作业管理系统
- 🔄 讨论区功能
- 🔄 前端界面开发

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/87361/Edu_Cloud/issues)
- 邮箱: 1316757358@qq.com

---

