# 📖 人脸签到考勤系统 - API 接口文档

> **版本**：v1.1  
> **基础路径**：`http://localhost:8081/api`  
> **数据格式**：JSON  
> **编码**：UTF-8  
> **更新日期**：2026-01-09

---

## 📋 目录

1. [通用说明](#通用说明)
2. [员工管理接口](#员工管理接口)
3. [人脸注册接口](#人脸注册接口)
4. [签到考勤接口](#签到考勤接口)
5. [考勤记录接口](#考勤记录接口)
6. [统计报表接口](#统计报表接口)
7. [数据模型](#数据模型)

---

## 🔧 通用说明

### 响应格式

所有接口统一返回以下格式：

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 人脸检测失败 |
| 500 | 服务器内部错误 |

---

## 👤 员工管理接口

### 1. 获取员工列表

**接口地址**：`GET /employees`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | String | 否 | 搜索关键词（工号/姓名） |
| department | String | 否 | 部门筛选 |
| page | Integer | 否 | 页码，默认1 |
| size | Integer | 否 | 每页数量，默认20 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 50,
    "page": 1,
    "size": 20,
    "list": [
      {
        "id": 1,
        "employeeId": "EMP001",
        "name": "张三",
        "department": "技术部",
        "position": "工程师",
        "hasFace": true,
        "faceImage": "/uploads/faces/EMP001.jpg",
        "createdAt": "2026-01-09T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取单个员工

**接口地址**：`GET /employees/{employeeId}`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "employeeId": "EMP001",
    "name": "张三",
    "department": "技术部",
    "position": "工程师",
    "hasFace": true,
    "faceImage": "/uploads/faces/EMP001.jpg",
    "createdAt": "2026-01-09T10:00:00",
    "updatedAt": "2026-01-09T10:00:00"
  }
}
```

---

### 3. 添加员工

**接口地址**：`POST /employees`

**请求体**：
```json
{
  "employeeId": "EMP001",
  "name": "张三",
  "department": "技术部",
  "position": "工程师"
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| employeeId | String | 是 | 工号，唯一标识 |
| name | String | 是 | 姓名 |
| department | String | 否 | 部门 |
| position | String | 否 | 职位 |

**响应示例**：
```json
{
  "success": true,
  "code": 201,
  "message": "添加成功",
  "data": {
    "id": 1,
    "employeeId": "EMP001",
    "name": "张三",
    "department": "技术部",
    "position": "工程师",
    "hasFace": false,
    "createdAt": "2026-01-09T10:00:00"
  }
}
```

---

### 4. 更新员工信息

**接口地址**：`PUT /employees/{employeeId}`

**请求体**：
```json
{
  "name": "张三三",
  "department": "研发部",
  "position": "高级工程师"
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "更新成功",
  "data": { ... }
}
```

---

### 5. 删除员工

**接口地址**：`DELETE /employees/{employeeId}`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

> **注意**：删除员工会同时删除其人脸数据和考勤记录。

---

## 🎭 人脸注册接口

### 1. 上传人脸照片

**接口地址**：`POST /face/upload`

**请求格式**：`multipart/form-data`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| employeeId | String | 是 | 工号 |
| image | File | 是 | 人脸照片（JPG/PNG） |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "人脸检测成功",
  "data": {
    "faceDetected": true,
    "faceCount": 1,
    "faceLocation": {
      "top": 100,
      "right": 300,
      "bottom": 350,
      "left": 150
    },
    "imageUrl": "/uploads/temp/abc123.jpg"
  }
}
```

**错误响应**：
```json
{
  "success": false,
  "code": 422,
  "message": "未检测到人脸，请调整拍摄角度",
  "data": null
}
```

---

### 2. 确认注册人脸

**接口地址**：`POST /face/register`

**请求体**：
```json
{
  "employeeId": "EMP001",
  "imageUrls": [
    "/uploads/temp/abc123.jpg",
    "/uploads/temp/abc124.jpg",
    "/uploads/temp/abc125.jpg"
  ]
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| employeeId | String | 是 | 工号 |
| imageUrls | Array | 是 | 已上传的人脸照片URL列表 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "人脸注册成功",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "faceImage": "/uploads/faces/EMP001.jpg",
    "registeredAt": "2026-01-09T10:30:00"
  }
}
```

---

### 3. 实时人脸检测（Base64）

**接口地址**：`POST /face/detect`

**请求体**：
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "检测成功",
  "data": {
    "faceDetected": true,
    "faceCount": 1,
    "faces": [
      {
        "location": {
          "top": 100,
          "right": 300,
          "bottom": 350,
          "left": 150
        },
        "quality": 0.95
      }
    ]
  }
}
```

---

### 4. 删除人脸数据

**接口地址**：`DELETE /face/{employeeId}`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "人脸数据已删除",
  "data": null
}
```

---

## ✅ 签到考勤接口

### 1. 人脸签到

**接口地址**：`POST /attendance/check-in`

**请求体**：
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**响应示例（成功）**：
```json
{
  "success": true,
  "code": 200,
  "message": "签到成功",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "department": "技术部",
    "checkInTime": "2026-01-09T09:00:15",
    "status": "正常",
    "similarity": 0.92,
    "faceImage": "/uploads/faces/EMP001.jpg"
  }
}
```

**响应示例（迟到）**：
```json
{
  "success": true,
  "code": 200,
  "message": "签到成功（迟到）",
  "data": {
    "employeeId": "EMP002",
    "name": "李四",
    "department": "市场部",
    "checkInTime": "2026-01-09T09:25:30",
    "status": "迟到",
    "lateMinutes": 25,
    "similarity": 0.89
  }
}
```

**响应示例（未识别）**：
```json
{
  "success": false,
  "code": 404,
  "message": "未识别到已注册的人脸",
  "data": {
    "faceDetected": true,
    "suggestion": "请确认是否已注册人脸，或调整光线和角度重试"
  }
}
```

**响应示例（重复签到）**：
```json
{
  "success": false,
  "code": 400,
  "message": "今日已签到",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "checkInTime": "2026-01-09T09:00:15"
  }
}
```

---

### 2. 人脸签退

**接口地址**：`POST /attendance/check-out`

**请求体**：
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**响应示例（成功）**：
```json
{
  "success": true,
  "code": 200,
  "message": "签退成功",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "checkOutTime": "2026-01-09T18:05:20",
    "status": "正常",
    "workHours": "9小时5分钟"
  }
}
```

**响应示例（早退）**：
```json
{
  "success": true,
  "code": 200,
  "message": "签退成功（早退）",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "checkOutTime": "2026-01-09T17:30:00",
    "status": "早退",
    "earlyMinutes": 30
  }
}
```

---

### 3. 获取今日签到状态

**接口地址**：`GET /attendance/today`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| employeeId | String | 否 | 指定员工工号 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "date": "2026-01-09",
    "totalEmployees": 30,
    "checkedIn": 25,
    "checkedOut": 10,
    "records": [
      {
        "employeeId": "EMP001",
        "name": "张三",
        "department": "技术部",
        "checkInTime": "09:00:15",
        "checkOutTime": null,
        "status": "已签到"
      }
    ]
  }
}
```

---

## 📋 考勤记录接口

### 1. 查询考勤记录

**接口地址**：`GET /attendance/records`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startDate | String | 否 | 开始日期（YYYY-MM-DD） |
| endDate | String | 否 | 结束日期（YYYY-MM-DD） |
| employeeId | String | 否 | 员工工号 |
| department | String | 否 | 部门 |
| status | String | 否 | 状态（正常/迟到/早退/缺勤） |
| includeAbsent | Boolean | 否 | 是否包含缺勤人员（仅单日查询有效） |
| page | Integer | 否 | 页码 |
| size | Integer | 否 | 每页数量 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "list": [
      {
        "id": 1,
        "employeeId": "EMP001",
        "name": "张三",
        "department": "技术部",
        "date": "2026-01-09",
        "checkInTime": "09:00:15",
        "checkOutTime": "18:05:20",
        "checkInStatus": "正常",
        "checkOutStatus": "正常",
        "workHours": "9小时5分钟"
      },
      {
        "id": 2,
        "employeeId": "EMP002",
        "name": "李四",
        "department": "市场部",
        "date": "2026-01-09",
        "checkInTime": "09:25:30",
        "checkOutTime": "17:30:00",
        "checkInStatus": "迟到",
        "checkOutStatus": "早退",
        "workHours": "8小时4分钟"
      },
      {
        "id": 3,
        "employeeId": "EMP003",
        "name": "王五",
        "department": "技术部",
        "date": "2026-01-09",
        "checkInTime": null,
        "checkOutTime": null,
        "checkInStatus": "缺勤",
        "checkOutStatus": null,
        "workHours": null
      }
    ]
  }
}
```

---

### 2. 获取员工考勤详情

**接口地址**：`GET /attendance/records/{employeeId}`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| month | String | 否 | 月份（YYYY-MM），默认当月 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "employeeId": "EMP001",
    "name": "张三",
    "department": "技术部",
    "month": "2026-01",
    "summary": {
      "workDays": 22,
      "actualDays": 20,
      "lateDays": 2,
      "earlyDays": 0,
      "absentDays": 2,
      "attendanceRate": "90.9%"
    },
    "records": [
      {
        "date": "2026-01-09",
        "checkInTime": "09:00:15",
        "checkOutTime": "18:05:20",
        "status": "正常"
      }
    ]
  }
}
```

---

### 3. 导出考勤记录

**接口地址**：`GET /attendance/export`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startDate | String | 是 | 开始日期 |
| endDate | String | 是 | 结束日期 |
| format | String | 否 | 导出格式（excel/csv），默认excel |

**响应**：返回文件下载

---

## 📊 统计报表接口

### 1. 获取考勤统计

**接口地址**：`GET /statistics/attendance`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startDate | String | 否 | 开始日期 |
| endDate | String | 否 | 结束日期 |
| department | String | 否 | 部门筛选 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "period": {
      "startDate": "2026-01-01",
      "endDate": "2026-01-09"
    },
    "overview": {
      "totalEmployees": 30,
      "totalWorkDays": 7,
      "avgAttendanceRate": "95.2%",
      "totalLateCount": 15,
      "totalEarlyCount": 5,
      "totalAbsentCount": 3
    },
    "dailyStats": [
      {
        "date": "2026-01-09",
        "checkedIn": 28,
        "lateCount": 3,
        "absentCount": 2,
        "attendanceRate": "93.3%"
      }
    ],
    "departmentStats": [
      {
        "department": "技术部",
        "employeeCount": 10,
        "attendanceRate": "98.0%",
        "lateCount": 2
      }
    ]
  }
}
```

---

### 2. 获取今日概览

**接口地址**：`GET /statistics/today`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "date": "2026-01-09",
    "currentTime": "14:30:00",
    "totalEmployees": 30,
    "checkedIn": 28,
    "notCheckedIn": 2,
    "checkedOut": 0,
    "lateCount": 3,
    "attendanceRate": "93.3%",
    "recentRecords": [
      {
        "employeeId": "EMP001",
        "name": "张三",
        "action": "签到",
        "time": "09:00:15",
        "status": "正常"
      }
    ]
  }
}
```

---

## ⚙️ 系统设置接口

### 1. 获取考勤设置

**接口地址**：`GET /settings/attendance`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "workStartTime": "09:00",
    "workEndTime": "18:00",
    "lateThreshold": 10,
    "earlyThreshold": 10,
    "recognitionThreshold": 0.5
  }
}
```

---

### 2. 更新考勤设置

**接口地址**：`PUT /settings/attendance`

**请求体**：
```json
{
  "workStartTime": "09:00",
  "workEndTime": "18:00",
  "lateThreshold": 15,
  "earlyThreshold": 15,
  "recognitionThreshold": 0.5
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "设置已保存",
  "data": { ... }
}
```

---

## 📦 数据模型

### Employee（员工实体）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| employeeId | String | 工号（唯一） |
| name | String | 姓名 |
| department | String | 部门 |
| position | String | 职位 |
| faceEncoding | Binary | 人脸特征向量（128维） |
| faceImage | String | 人脸照片路径 |
| createdAt | DateTime | 创建时间 |
| updatedAt | DateTime | 更新时间 |

### Attendance（考勤记录）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| employeeId | String | 工号（外键） |
| date | Date | 日期 |
| checkInTime | DateTime | 签到时间 |
| checkOutTime | DateTime | 签退时间 |
| checkInStatus | String | 签到状态（正常/迟到） |
| checkOutStatus | String | 签退状态（正常/早退） |
| checkInImage | String | 签到截图路径 |
| createdAt | DateTime | 创建时间 |

---

## 🗃️ 数据库设计

### 创建数据库

```sql
-- SQLite 数据库

-- 员工表
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    department TEXT,
    position TEXT,
    face_encoding BLOB,        -- LBP特征编码（二进制）
    face_image TEXT,           -- 人脸照片路径
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 考勤记录表
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    date DATE NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    check_in_status TEXT DEFAULT '正常',   -- 签到状态：正常/迟到
    check_out_status TEXT,                 -- 签退状态：正常/早退
    check_in_image TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    UNIQUE(employee_id, date)
);

-- 系统设置表
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

-- 初始化设置
INSERT INTO settings (key, value) VALUES
    ('work_start_time', '09:00'),
    ('work_end_time', '18:00'),
    ('late_threshold', '10'),      -- 迟到容忍分钟数
    ('early_threshold', '10'),     -- 早退容忍分钟数
    ('recognition_threshold', '0.5');  -- 人脸识别相似度阈值
```

### 状态说明

| 字段 | 状态值 | 说明 |
|------|--------|------|
| checkInStatus | 正常 | 在规定时间内签到 |
| checkInStatus | 迟到 | 超过上班时间+容忍时间后签到 |
| checkInStatus | 缺勤 | 当天未签到（虚拟状态，查询时生成） |
| checkOutStatus | 正常 | 在规定时间后签退 |
| checkOutStatus | 早退 | 在下班时间-容忍时间前签退 |

---

## ⚠️ 注意事项

1. **图片格式** - 支持 JPG、PNG 格式，建议不超过 2MB
2. **Base64编码** - 前端通过摄像头获取的图片需转为Base64格式
3. **人脸检测** - 每张图片只处理检测到的第一张人脸
4. **识别阈值** - 默认0.5，可在设置中调整（越小越严格）
5. **重复签到** - 同一天同一员工只能签到一次
6. **CORS跨域** - 后端已配置允许本地访问

---

## 📝 更新记录

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-01-09 | v1.0 | 初始版本 |
