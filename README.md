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
- **现代化架构**: 基于FastAPI构建的高性能API
- **数据库支持**: SQLAlchemy ORM，支持SQLite/PostgreSQL
- **用户认证**: 安全的用户认证和会话管理
- **API文档**: 自动生成的Swagger文档

## 🛠 技术栈

### 后端技术
- **语言**: Python 3.12+
- **框架**: FastAPI (现代化Web框架，内置数据验证)
- **数据库**: SQLAlchemy ORM
- **依赖管理**: pyproject.toml + uv
- **认证**: 基于BUPT_Middleware的CAS/UC集成

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
│       │   ├── config.py          # 配置管理
│       │   ├── database.py        # 数据库连接
│       │   └── security.py        # 安全相关
│       ├── user/                  # 用户模块
│       │   ├── __init__.py
│       │   ├── api.py            # 用户API路由
│       │   ├── models.py         # 用户数据模型
│       │   └── schemas.py        # 用户数据验证
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
└── README.md                     # 项目文档
```

## 🚀 快速开始

### 环境要求
- Python 3.12+
- uv (现代Python包管理工具)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
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
   ```

4. **安装项目包**
   ```bash
   uv pip install -e .
   ```

5. **启动应用**
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **访问应用**
   - API文档: http://localhost:8000/docs
   - 应用首页: http://localhost:8000

## 📖 API文档

启动应用后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

- `GET /` - 应用首页
- `GET /docs` - Swagger API文档
- `/api/user/*` - 用户相关API
- `/api/course/*` - 课程相关API (开发中)
- `/api/assignment/*` - 作业相关API (开发中)

## 🔧 开发指南

### 添加新模块

1. 在 `src/edu_cloud/` 下创建新模块目录
2. 创建必要的文件：`__init__.py`, `api.py`, `models.py`, `schemas.py`
3. 在 `main.py` 中注册新的API路由

### 数据库操作

```python
# 创建数据库表
Base.metadata.create_all(bind=engine)

# 获取数据库会话
db: Session = next(get_db())
```

### 添加新的API端点

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from edu_cloud.common.database import get_db

router = APIRouter()

@router.get("/example")
def get_example(db: Session = Depends(get_db)):
    return {"message": "Example endpoint"}
```

## 🔐 安全考虑

- 使用环境变量管理敏感配置
- 实现了基于JWT的用户认证
- 数据库连接使用SQLAlchemy ORM防止SQL注入
- API端点适当的权限验证

## 📋 开发原则

### 技术约束
1. **Python优先**: 所有核心功能使用Python实现
2. **前端验证**: 前端主要用于展示后端功能，UI追求快速实现
3. **认证分离**: BUPT_Middleware只负责认证，数据抓取由项目自己实现

### 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8代码风格
- 模块化设计，职责分离
- 完善的错误处理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v0.1.0 (当前版本)
- ✅ 项目初始化
- ✅ 用户认证系统基础架构
- ✅ 数据库配置和模型
- ✅ FastAPI应用框架搭建
- ✅ 基础API端点

### 计划功能
- 🔄 用户注册/登录完整实现
- 🔄 课程管理系统
- 🔄 作业管理系统
- 🔄 讨论区功能
- 🔄 前端界面开发

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 这是一个教育项目，旨在学习和实践现代Web开发技术。请遵守相关法律法规和学校规定。
