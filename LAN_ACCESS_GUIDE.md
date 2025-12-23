# 局域网远程访问配置指南

本指南将帮助您配置系统，使同一局域网内的其他电脑可以访问后端服务。

## 📋 前置条件

1. **确保所有设备在同一局域网内**
   - 所有电脑连接到同一个WiFi或路由器
   - 确保网络连接正常

2. **获取服务器IP地址**
   - 在运行后端的电脑上执行以下命令获取IP地址：

   **Linux/Mac:**
   ```bash
   hostname -I
   # 或
   ip addr show | grep "inet " | grep -v "127.0.0.1"
   ```

   **Windows:**
   ```cmd
   ipconfig
   # 查找 "IPv4 地址"，通常是 192.168.x.x 或 10.x.x.x
   ```

   示例IP地址：`192.168.1.100` 或 `10.129.27.34`

## 🔧 配置步骤

### 步骤1：确认后端配置（服务器端）

后端默认配置已经正确，监听地址为 `0.0.0.0`（所有网络接口）。

检查 `src/edu_cloud/common/config.py`：
```python
host: str = "0.0.0.0"  # ✅ 已正确配置
port: int = 5000
```

如果配置正确，直接启动后端：
```bash
python main.py
```

后端会显示：
```
 * Running on http://0.0.0.0:5000
```

### 步骤2：配置防火墙（服务器端）

**Linux (Ubuntu/Debian):**
```bash
# 允许5000端口
sudo ufw allow 5000/tcp
# 或临时关闭防火墙（仅用于测试）
sudo ufw disable
```

**Linux (CentOS/RHEL):**
```bash
# 允许5000端口
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

**Windows:**
1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 选择"入站规则" → "新建规则"
4. 选择"端口" → "TCP" → 输入端口 `5000`
5. 允许连接，应用到所有配置文件

**Mac:**
```bash
# 允许5000端口
sudo pfctl -f /etc/pf.conf
# 或通过系统偏好设置 → 安全性与隐私 → 防火墙 → 选项
```

### 步骤3：配置客户端（其他电脑）

在其他电脑上，需要修改GUI应用的API地址配置。

#### 方法1：通过环境变量（推荐）

在启动GUI应用前设置环境变量：

**Linux/Mac:**
```bash
export EDU_CLOUD_API_URL=http://<服务器IP>:5000
python start_gui.py
```

**Windows (CMD):**
```cmd
set EDU_CLOUD_API_URL=http://<服务器IP>:5000
python start_gui.py
```

**Windows (PowerShell):**
```powershell
$env:EDU_CLOUD_API_URL="http://<服务器IP>:5000"
python start_gui.py
```

#### 方法2：修改配置文件

GUI应用的配置文件位于：`~/.edu_cloud_gui/config.json`

**Linux/Mac:**
```bash
mkdir -p ~/.edu_cloud_gui
cat > ~/.edu_cloud_gui/config.json << EOF
{
  "api_base_url": "http://<服务器IP>:5000",
  "api_timeout": 30
}
EOF
```

**Windows:**
配置文件位置：`C:\Users\<用户名>\.edu_cloud_gui\config.json`

创建文件并写入：
```json
{
  "api_base_url": "http://<服务器IP>:5000",
  "api_timeout": 30
}
```

将 `<服务器IP>` 替换为实际的服务器IP地址，例如：
- `http://192.168.1.100:5000`
- `http://10.129.27.34:5000`

#### 方法3：在代码中修改（临时测试）

编辑 `gui/config.py`，修改默认值：
```python
self.api_base_url = os.getenv("EDU_CLOUD_API_URL", "http://<服务器IP>:5000")
```

## ✅ 验证配置

### 在服务器端验证

1. 启动后端服务：
   ```bash
   python main.py
   ```

2. 在服务器本地测试：
   ```bash
   curl http://localhost:5000/health
   ```

3. 使用局域网IP测试：
   ```bash
   curl http://<服务器IP>:5000/health
   ```

### 在客户端验证

1. 在浏览器中访问：
   ```
   http://<服务器IP>:5000/health
   ```

   应该返回：
   ```json
   {
     "status": "healthy",
     "service": "edu-cloud-api"
   }
   ```

2. 启动GUI应用，尝试登录

## 🔍 故障排查

### 问题1：无法连接到服务器

**检查项：**
- ✅ 确认服务器IP地址正确
- ✅ 确认后端服务正在运行
- ✅ 确认防火墙允许5000端口
- ✅ 确认客户端和服务器在同一局域网
- ✅ 尝试ping服务器IP：`ping <服务器IP>`

### 问题2：连接被拒绝

**可能原因：**
- 防火墙阻止了连接
- 后端没有监听 `0.0.0.0`

**解决方法：**
- 检查防火墙设置
- 确认 `src/edu_cloud/common/config.py` 中 `host = "0.0.0.0"`

### 问题3：CORS错误

如果遇到CORS错误，检查 `src/edu_cloud/common/config.py`：
```python
cors_origins: str = "*"  # 开发环境可以使用 *
```

生产环境建议设置为具体IP或域名：
```python
cors_origins: str = "http://<客户端IP>:<端口>,http://<服务器IP>:5000"
```

## 📝 快速参考

**服务器端（运行后端的电脑）：**
```bash
# 1. 获取IP地址
hostname -I

# 2. 启动后端（确保host=0.0.0.0）
python main.py

# 3. 开放防火墙端口（如果需要）
sudo ufw allow 5000/tcp
```

**客户端（其他电脑）：**
```bash
# 方法1：环境变量
export EDU_CLOUD_API_URL=http://<服务器IP>:5000
python start_gui.py

# 方法2：修改配置文件
# 编辑 ~/.edu_cloud_gui/config.json
```

## 🔒 安全建议

1. **生产环境：**
   - 不要使用 `cors_origins: "*"`
   - 设置具体的允许来源
   - 使用HTTPS（需要配置SSL证书）
   - 限制防火墙规则，只允许必要的IP访问

2. **开发环境：**
   - 仅在受信任的局域网内使用
   - 测试完成后关闭远程访问

3. **密码安全：**
   - 使用强密码
   - 定期更换密码

## 📞 示例配置

假设服务器IP为 `192.168.1.100`：

**服务器端：**
```bash
# 启动后端
python main.py
# 输出：Running on http://0.0.0.0:5000
```

**客户端：**
```bash
# 设置环境变量
export EDU_CLOUD_API_URL=http://192.168.1.100:5000

# 启动GUI
python start_gui.py
```

或在配置文件中：
```json
{
  "api_base_url": "http://192.168.1.100:5000",
  "api_timeout": 30
}
```

---

**注意：** 如果服务器IP地址发生变化（例如重新连接WiFi），需要更新客户端配置。

