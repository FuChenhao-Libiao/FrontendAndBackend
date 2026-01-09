# 🎭 人脸签到考勤系统

基于 Python + FastAPI + OpenCV 的人脸识别考勤系统。

## ✨ 功能特性

- ✅ 人脸注册 - 摄像头拍照采集人脸
- ✅ 人脸签到/签退 - 实时识别打卡
- ✅ 员工管理 - 增删改查
- ✅ 考勤记录 - 分页查询、多条件筛选
- ✅ 考勤统计 - 今日应到、已签到、迟到、早退、缺勤
- ✅ 状态分离 - 签到状态和签退状态独立记录
- ✅ 系统设置 - 上下班时间、容忍分钟数配置

## 📁 项目结构

```
人脸签到考勤系统/
├── backend/                # 后端代码
│   ├── app.py              # FastAPI 主应用（包含所有API路由）
│   ├── config.py           # 配置文件
│   ├── database.py         # SQLite 数据库操作
│   ├── face_service.py     # 人脸检测和识别服务
│   ├── start_server.bat    # Windows 启动脚本
│   ├── data/               # 数据目录
│   │   └── attendance.db   # SQLite 数据库
│   └── faces/              # 人脸照片存储
├── frontend/               # 前端代码
│   ├── index.html          # 签到打卡页
│   ├── register.html       # 人脸注册页
│   ├── records.html        # 考勤记录页
│   ├── admin.html          # 管理后台页
│   └── js/
│       └── api.js          # API 接口封装
├── 项目思路文档.md
└── API接口文档.md
```

## 🚀 快速开始

### 1. 安装依赖

确保已安装 Python 3.9+，然后安装依赖：

```bash
cd backend
pip install fastapi uvicorn opencv-python numpy
```

### 2. 启动后端服务

**方式一：使用启动脚本（推荐）**

双击 `backend/start_server.bat`

**方式二：命令行启动**

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8081
```

服务启动后访问：
- API 服务：http://localhost:8081
- API 文档：http://localhost:8081/docs

### 3. 访问前端页面

直接用浏览器打开 `frontend/index.html`，或使用 VS Code 的 Live Server 插件。

## 📖 使用说明

### 签到打卡
- 打开摄像头实时显示画面
- 点击"签到"或"签退"按钮
- 系统自动识别人脸并记录
- 显示签到状态：正常/迟到

### 人脸注册
1. 选择已有员工或添加新员工
2. 拍摄照片采集人脸
3. 确认注册

### 考勤记录
- 按日期、员工、部门、状态筛选
- 单日查询自动显示缺勤人员
- 分开显示签到状态和签退状态

### 管理后台
- 员工管理：增删改查
- 系统设置：上下班时间、迟到/早退阈值等

## ⚙️ 配置说明

编辑 `backend/config.py` 修改配置：

```python
# 默认设置
DEFAULT_SETTINGS = {
    "work_start_time": "09:00",    # 上班时间
    "work_end_time": "18:00",      # 下班时间
    "late_threshold": 10,          # 迟到容忍（分钟）
    "early_threshold": 10,         # 早退容忍（分钟）
    "recognition_threshold": 0.5,  # 识别阈值（0-1，越大越宽松）
}
```

## 🔧 常见问题

### 1. 摄像头无法访问

- 确保浏览器有摄像头权限
- 使用 HTTPS 或 localhost 访问（浏览器安全限制）
- 检查是否有其他程序占用摄像头

### 2. 识别不准确

- 调整 `recognition_threshold` 值（0.3-0.7）
- 注册时确保光线充足、人脸清晰
- 尝试重新注册人脸

### 3. 后端服务无法启动

- 确保端口 8081 未被占用
- 检查 Python 环境是否正确
- 查看终端错误信息

## 📝 技术栈

| 类型 | 技术 |
|------|------|
| 后端 | Python 3.11, FastAPI, Uvicorn |
| 数据库 | SQLite |
| 人脸检测 | OpenCV Haar Cascade |
| 特征编码 | LBP (Local Binary Patterns) |
| 人脸比对 | 余弦相似度 |
| 前端 | HTML5, CSS3, JavaScript |
| 摄像头 | WebRTC |

## 📄 License

MIT License
