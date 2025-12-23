# Git 测试分支使用指南

本指南说明如何使用Git测试分支来测试新功能。

## 📋 Git测试版本管理方式

Git通常有几种方式处理测试版本：

### 方式1：测试分支（推荐）
- **优点**：灵活，可以持续更新，不影响主分支
- **适用**：功能开发、测试阶段
- **分支命名**：`test/lan-access`、`feature/lan-access`、`dev/lan-access`

### 方式2：Git标签（Tag）
- **优点**：标记特定版本，便于回滚
- **适用**：稳定版本发布
- **标签命名**：`v1.0.0-test`、`lan-access-v1.0`

### 方式3：Release分支
- **优点**：正式发布前的准备
- **适用**：准备发布正式版本
- **分支命名**：`release/v1.0.0`

## 🚀 当前项目：使用测试分支

我们使用**测试分支**方式，创建 `test/lan-access` 分支。

## 📝 操作步骤

### 在开发电脑上（当前电脑）

#### 1. 提交当前更改
```bash
# 添加所有更改
git add LAN_ACCESS_GUIDE.md configure_lan_access.py README.md

# 提交更改
git commit -m "feat: 添加局域网访问功能和配置工具"
```

#### 2. 创建并切换到测试分支
```bash
# 从当前main分支创建测试分支
git checkout -b test/lan-access

# 或者如果分支已存在，直接切换
git checkout test/lan-access
```

#### 3. 推送测试分支到远程
```bash
# 推送分支到远程仓库
git push -u origin test/lan-access

# 如果远程已有同名分支，强制推送（谨慎使用）
# git push -u origin test/lan-access --force
```

### 在其他测试电脑上

#### 方法1：克隆并切换到测试分支（推荐）
```bash
# 克隆仓库
git clone https://github.com/87361/Edu_Cloud.git
cd Edu_Cloud

# 切换到测试分支
git checkout test/lan-access

# 如果分支不存在，先获取远程分支
git fetch origin
git checkout -b test/lan-access origin/test/lan-access
```

#### 方法2：直接克隆测试分支
```bash
# 只克隆测试分支（节省空间）
git clone -b test/lan-access --single-branch https://github.com/87361/Edu_Cloud.git
cd Edu_Cloud
```

#### 方法3：在已有仓库中切换
```bash
# 如果已经克隆了仓库
cd Edu_Cloud

# 获取最新分支信息
git fetch origin

# 切换到测试分支
git checkout test/lan-access

# 更新到最新
git pull origin test/lan-access
```

## 🔄 更新测试分支

### 在开发电脑上更新测试分支
```bash
# 切换到测试分支
git checkout test/lan-access

# 合并main分支的最新更改（如果需要）
git merge main

# 或者直接提交新更改
git add .
git commit -m "fix: 修复xxx问题"
git push origin test/lan-access
```

### 在测试电脑上更新
```bash
# 切换到测试分支
git checkout test/lan-access

# 拉取最新更改
git pull origin test/lan-access
```

## 🏷️ 使用Git标签（可选）

如果需要标记特定测试版本：

### 创建标签
```bash
# 切换到测试分支
git checkout test/lan-access

# 创建标签
git tag -a v1.0.0-lan-access -m "局域网访问功能测试版本"

# 推送标签到远程
git push origin v1.0.0-lan-access
```

### 使用标签
```bash
# 克隆并切换到特定标签
git clone https://github.com/87361/Edu_Cloud.git
cd Edu_Cloud
git checkout v1.0.0-lan-access
```

## 📊 分支管理策略

### 推荐的工作流程

```
main (主分支)
  ├── test/lan-access (测试分支) ← 当前测试
  ├── feature/xxx (功能分支)
  └── release/v1.0 (发布分支)
```

### 分支命名规范

- **测试分支**：`test/<功能名>` 或 `test/<版本号>`
- **功能分支**：`feature/<功能名>`
- **修复分支**：`fix/<问题描述>`
- **发布分支**：`release/v<版本号>`

## ✅ 测试完成后

### 合并到主分支
```bash
# 切换到主分支
git checkout main

# 合并测试分支
git merge test/lan-access

# 推送主分支
git push origin main

# 删除测试分支（可选）
git branch -d test/lan-access
git push origin --delete test/lan-access
```

## 🔍 查看分支信息

```bash
# 查看所有分支
git branch -a

# 查看远程分支
git branch -r

# 查看分支提交历史
git log test/lan-access --oneline

# 查看分支差异
git diff main..test/lan-access
```

## 📝 快速参考

**开发电脑：**
```bash
git add .
git commit -m "feat: 添加局域网访问功能"
git checkout -b test/lan-access
git push -u origin test/lan-access
```

**测试电脑：**
```bash
git clone -b test/lan-access https://github.com/87361/Edu_Cloud.git
cd Edu_Cloud
```

**更新测试版本：**
```bash
# 开发电脑
git checkout test/lan-access
git add .
git commit -m "fix: 修复问题"
git push origin test/lan-access

# 测试电脑
git checkout test/lan-access
git pull origin test/lan-access
```

## ⚠️ 注意事项

1. **不要强制推送主分支**：避免覆盖其他人的工作
2. **测试分支可以强制推送**：测试阶段可以灵活处理
3. **定期同步主分支**：保持测试分支与主分支同步
4. **测试完成后清理**：合并后删除测试分支

## 🎯 当前项目状态

- **主分支**：`main`
- **测试分支**：`test/lan-access`（待创建）
- **远程仓库**：`https://github.com/87361/Edu_Cloud.git`

