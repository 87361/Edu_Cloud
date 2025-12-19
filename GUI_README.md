# GUI应用使用说明

## 概述

这是一个基于CustomTkinter的前后端分离GUI客户端，用于访问云邮教学空间系统。

## 功能特性

- ✅ 用户登录（支持本地账号和CAS登录）
- ✅ 作业列表展示（支持筛选和排序）
- ✅ 作业详情查看
- ✅ 作业同步（从学校系统抓取）
- ✅ 作业提交（文件上传）
- ✅ Token自动管理（登录状态保持）

## 安装依赖

首先确保已安装项目依赖：

```bash
# 安装项目依赖（包括customtkinter）
pip install -e .
```

或者单独安装customtkinter：

```bash
pip install customtkinter>=5.2.0
```

## 启动应用

### 方式1：使用启动脚本（推荐）

```bash
python start_gui.py
```

### 方式2：直接运行主模块

```bash
python -m gui.main
```

## 配置

GUI应用默认连接到 `http://localhost:5000`。

如需修改API地址，可以通过以下方式：

1. **环境变量**：
   ```bash
   export EDU_CLOUD_API_URL=http://your-api-server:5000
   python start_gui.py
   ```

2. **配置文件**：
   配置文件位于 `~/.edu_cloud_gui/config.json`，可以手动编辑：
   ```json
   {
     "api_base_url": "http://your-api-server:5000",
     "api_timeout": 30
   }
   ```

## 使用流程

1. **启动后端服务**：
   ```bash
   python main.py
   ```

2. **启动GUI应用**：
   ```bash
   python start_gui.py
   ```

3. **登录**：
   - 选择登录方式（本地账号或CAS登录）
   - 输入用户名/学号和密码
   - 点击"登录"按钮

4. **查看作业**：
   - 登录成功后自动显示作业列表
   - 可以筛选（全部/未提交/已提交）
   - 双击作业项查看详情

5. **同步作业**：
   - 点击"同步作业"按钮
   - 输入学校账号（学号）和密码
   - 等待同步完成

6. **提交作业**：
   - 在作业详情页面点击"浏览..."选择文件
   - 选择.zip文件
   - 点击"提交作业"按钮

## 项目结构

```
gui/
├── __init__.py
├── main.py                    # 主应用入口
├── config.py                 # 配置管理
├── api_client.py             # API客户端
├── views/                    # 界面视图
│   ├── login_view.py         # 登录界面
│   ├── assignment_list_view.py  # 作业列表界面
│   └── assignment_detail_view.py # 作业详情界面
└── utils/                    # 工具模块
    └── token_manager.py      # Token管理
```

## 注意事项

1. **后端服务**：确保后端API服务（`main.py`）已启动并运行在配置的地址上

2. **Token管理**：Token存储在 `~/.edu_cloud_gui/token.txt`，自动管理过期和刷新

3. **作业提交**：如果后端尚未实现提交接口，GUI会显示提示信息，但文件选择功能已实现

4. **网络连接**：GUI应用需要网络连接到后端API，请确保网络畅通

## 故障排除

### 问题：无法连接到服务器

- 检查后端服务是否已启动
- 检查API地址配置是否正确
- 检查防火墙设置

### 问题：登录失败

- 检查用户名和密码是否正确
- 检查后端服务是否正常运行
- 查看后端日志获取详细错误信息

### 问题：作业列表为空

- 点击"同步作业"按钮从学校系统同步
- 检查筛选条件是否正确
- 检查后端数据库是否有数据

## 开发说明

GUI应用完全独立于后端，通过HTTP API进行通信。所有API调用都封装在 `api_client.py` 中，便于维护和测试。

如需扩展功能，可以：
1. 在 `api_client.py` 中添加新的API方法
2. 在 `views/` 目录下创建新的视图
3. 在 `main.py` 中添加视图切换逻辑


