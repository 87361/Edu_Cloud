# 性能优化说明

## 问题诊断

在同一台电脑运行前后端时出现卡顿/闪退的主要原因：

### 1. GUI主线程阻塞（已修复）✅

**问题**：所有API请求（登录、获取作业列表、同步作业等）都在GUI主线程中同步执行，导致界面完全冻结。

**影响**：
- 登录时界面卡死
- 同步作业时（可能需要几十秒）界面完全无响应
- 用户无法进行任何操作

**解决方案**：
- ✅ 所有API调用改为在后台线程执行
- ✅ 使用`threading.Thread`创建后台线程
- ✅ 通过`self.after(0, callback)`在主线程中更新UI
- ✅ 确保线程安全，所有UI更新都在主线程执行

### 2. 后端同步操作耗时（建议优化）

**问题**：同步作业操作需要：
- 登录学校系统
- 抓取所有课程
- 遍历每门课程抓取作业
- 数据库查询和更新

**影响**：
- 如果使用Flask默认单线程模式，会阻塞其他请求
- 数据库操作在循环中执行，效率较低

**建议优化**（可选）：
- 使用Flask的线程模式或多进程模式
- 批量数据库操作（bulk insert/update）
- 添加进度反馈机制

## 已实施的优化

### GUI端优化

1. **登录操作** (`gui/views/login_view.py`)
   - ✅ 在后台线程执行登录请求
   - ✅ 主线程保持响应

2. **作业列表加载** (`gui/views/assignment_list_view.py`)
   - ✅ 用户信息加载在后台线程
   - ✅ 作业列表刷新在后台线程
   - ✅ UI更新在主线程

3. **同步作业** (`gui/views/assignment_list_view.py`)
   - ✅ 同步操作在后台线程执行（这是最耗时的操作）
   - ✅ 显示"同步中"状态提示
   - ✅ 完成后自动刷新列表

4. **作业详情和提交** (`gui/views/assignment_detail_view.py`)
   - ✅ 作业详情加载在后台线程
   - ✅ 文件提交在后台线程
   - ✅ 避免大文件上传时界面卡死

### 代码改进

所有网络请求都遵循以下模式：

```python
def do_operation():
    """在后台线程执行"""
    try:
        result = api_client.some_operation()
        # 在主线程更新UI
        self.after(0, lambda: self._on_success(result))
    except Exception as e:
        self.after(0, lambda: self._on_error(str(e)))

# 启动后台线程
thread = threading.Thread(target=do_operation, daemon=True)
thread.start()
```

## 性能提升

优化后的效果：
- ✅ GUI界面始终保持响应
- ✅ 长时间操作（如同步作业）不会冻结界面
- ✅ 用户可以随时取消或进行其他操作
- ✅ 资源占用更合理（不会因为阻塞导致资源堆积）

## 进一步优化建议

### 1. 后端优化（可选）

如果后端也需要优化，可以考虑：

```python
# 在main.py中使用多线程模式
if __name__ == '__main__':
    app = create_app()
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        threaded=True  # 启用多线程
    )
```

或者使用生产级WSGI服务器（如gunicorn）：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 2. 数据库优化（可选）

批量操作优化：

```python
# 批量插入而不是循环插入
db.bulk_insert_mappings(models.Assignment, assignments)
db.commit()
```

### 3. 添加请求超时

已在`gui/config.py`中设置了30秒超时，可以根据需要调整。

## 测试建议

1. **测试同步操作**：
   - 启动GUI应用
   - 点击"同步作业"
   - 观察界面是否保持响应
   - 可以尝试在同步过程中点击其他按钮

2. **测试并发操作**：
   - 同时打开多个GUI窗口（如果支持）
   - 观察资源占用情况

3. **监控资源使用**：
   ```bash
   # 监控CPU和内存
   top -p $(pgrep -f "python.*start_gui")
   ```

## 总结

主要性能问题已解决。GUI应用现在：
- ✅ 所有耗时操作都在后台线程执行
- ✅ 界面始终保持响应
- ✅ 不会因为网络请求阻塞而卡死
- ✅ 资源占用更合理

如果仍有性能问题，可能需要检查：
1. 后端服务器的配置（线程数、连接数等）
2. 数据库查询优化
3. 网络延迟问题

