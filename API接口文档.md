# 📖 书签管理器 - API 接口文档

> **版本**：v2.0  
> **基础路径**：`http://localhost:8080/api`  
> **数据格式**：JSON  
> **编码**：UTF-8  
> **认证方式**：JWT Bearer Token

---

## 📋 目录

1. [通用说明](#通用说明)
2. [用户认证接口](#用户认证接口)
3. [书签管理接口](#书签管理接口)
4. [分类管理接口](#分类管理接口)
5. [排序接口](#排序接口)
6. [数据管理接口](#数据管理接口)
7. [数据模型](#数据模型)

---

## 🔧 通用说明

### 请求头

**公开接口**（登录、注册）：
```
Content-Type: application/json
```

**需认证接口**（其他所有接口）：
```
Content-Type: application/json
Authorization: Bearer <token>
```

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

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | Boolean | 请求是否成功 |
| code | Integer | HTTP 状态码 |
| message | String | 提示信息 |
| data | Object/Array | 返回数据 |

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/Token无效 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 👤 用户认证接口

### 1. 用户注册

**接口地址**：`POST /auth/register`

**请求体**：
```json
{
  "username": "zhangsan",
  "password": "123456",
  "email": "zhangsan@example.com"
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名，3-20字符 |
| password | String | 是 | 密码，6-20字符 |
| email | String | 否 | 邮箱地址 |

**响应示例**：
```json
{
  "success": true,
  "code": 201,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar": "😀",
    "createdAt": "2026-01-06T10:00:00"
  }
}
```

> **注意**：新用户注册时会自动创建4个默认分类和8个示例书签。

---

### 2. 用户登录

**接口地址**：`POST /auth/login`

**请求体**：
```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar": "😀",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 86400
  }
}
```

---

### 3. 用户登出

**接口地址**：`POST /auth/logout`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

### 4. 获取当前用户信息

**接口地址**：`GET /auth/me`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar": "😀",
    "createdAt": "2026-01-06T10:00:00"
  }
}
```

---

### 5. 修改密码

**接口地址**：`PUT /auth/password`

**请求体**：
```json
{
  "currentPassword": "123456",
  "newPassword": "654321"
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| currentPassword | String | 是 | 当前密码 |
| newPassword | String | 是 | 新密码，6-20字符 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

---

### 6. 更新用户信息

**接口地址**：`PUT /auth/profile`

**请求体**：
```json
{
  "username": "newname",
  "avatar": "😎",
  "email": "newemail@example.com"
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 否 | 新用户名，3-20字符 |
| avatar | String | 否 | 头像（emoji） |
| email | String | 否 | 邮箱地址 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "信息更新成功",
  "data": {
    "id": 1,
    "username": "newname",
    "email": "newemail@example.com",
    "avatar": "😎",
    "createdAt": "2026-01-06T10:00:00"
  }
}
```

---

### 7. 获取用户设置

**接口地址**：`GET /auth/settings`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "theme": "light",
    "defaultView": "grid"
  }
}
```

---

### 8. 更新用户设置

**接口地址**：`PUT /auth/settings`

**请求体**：
```json
{
  "theme": "dark",
  "defaultView": "list"
}
```

**设置项说明**：

| 参数名 | 类型 | 可选值 | 说明 |
|--------|------|--------|------|
| theme | String | light / dark | 主题模式 |
| defaultView | String | grid / list | 默认视图 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "设置已保存",
  "data": {
    "theme": "dark",
    "defaultView": "list"
  }
}
```

---

### 9. 注销账户

**接口地址**：`DELETE /auth/account`

**请求体**：
```json
{
  "password": "123456"
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "账户已注销",
  "data": null
}
```

> **警告**：此操作将永久删除用户账户及所有数据（书签、分类、设置），无法恢复！

---

## 📑 书签管理接口

> ⚠️ 以下接口均需要在请求头中携带 Token

### 1. 获取书签列表

**接口地址**：`GET /bookmarks`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | Integer | 否 | 1 | 页码 |
| size | Integer | 否 | 100 | 每页数量 |
| categoryId | Long | 否 | - | 分类ID筛选 |
| keyword | String | 否 | - | 搜索关键词 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 100,
    "page": 1,
    "size": 100,
    "list": [
      {
        "id": 1,
        "title": "GitHub",
        "url": "https://github.com",
        "description": "代码托管平台",
        "favicon": "https://www.google.com/s2/favicons?domain=github.com&sz=64",
        "categoryId": 1,
        "categoryName": "开发工具",
        "sortOrder": 0,
        "createdAt": "2026-01-06T10:00:00",
        "updatedAt": "2026-01-06T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取单个书签

**接口地址**：`GET /bookmarks/{id}`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "title": "GitHub",
    "url": "https://github.com",
    "description": "代码托管平台",
    "favicon": "https://www.google.com/s2/favicons?domain=github.com&sz=64",
    "categoryId": 1,
    "categoryName": "开发工具",
    "sortOrder": 0,
    "createdAt": "2026-01-06T10:00:00",
    "updatedAt": "2026-01-06T10:00:00"
  }
}
```

---

### 3. 新增书签

**接口地址**：`POST /bookmarks`

**请求体**：
```json
{
  "title": "GitHub",
  "url": "https://github.com",
  "description": "代码托管平台",
  "categoryId": 1
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | String | 是 | 书签标题，最大100字符 |
| url | String | 是 | 网址，需要合法URL格式 |
| description | String | 否 | 描述，最大500字符 |
| categoryId | Long | 否 | 分类ID，不传为未分类 |

**响应示例**：
```json
{
  "success": true,
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 1,
    "title": "GitHub",
    "url": "https://github.com",
    "description": "代码托管平台",
    "favicon": "https://www.google.com/s2/favicons?domain=github.com&sz=64",
    "categoryId": 1,
    "categoryName": "开发工具",
    "sortOrder": 0,
    "createdAt": "2026-01-06T10:00:00",
    "updatedAt": "2026-01-06T10:00:00"
  }
}
```

> **说明**：favicon 由后端自动生成，使用 Google Favicon API。

---

### 4. 更新书签

**接口地址**：`PUT /bookmarks/{id}`

**请求体**：
```json
{
  "title": "GitHub - 全球最大代码托管平台",
  "url": "https://github.com",
  "description": "全球最大的代码托管平台",
  "categoryId": 1
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

### 5. 删除书签

**接口地址**：`DELETE /bookmarks/{id}`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 6. 批量删除书签

**接口地址**：`DELETE /bookmarks/batch`

**请求体**：
```json
{
  "ids": [1, 2, 3]
}
```

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "批量删除成功",
  "data": {
    "deletedCount": 3
  }
}
```

---

## 📁 分类管理接口

> ⚠️ 以下接口均需要在请求头中携带 Token

### 1. 获取分类列表

**接口地址**：`GET /categories`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "开发工具",
      "icon": "🔧",
      "bookmarkCount": 15,
      "sortOrder": 0,
      "createdAt": "2026-01-06T10:00:00"
    },
    {
      "id": 2,
      "name": "学习资源",
      "icon": "📚",
      "bookmarkCount": 8,
      "sortOrder": 1,
      "createdAt": "2026-01-06T10:00:00"
    }
  ]
}
```

---

### 2. 新增分类

**接口地址**：`POST /categories`

**请求体**：
```json
{
  "name": "开发工具",
  "icon": "🔧"
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | String | 是 | 分类名称，最大50字符 |
| icon | String | 否 | 分类图标（emoji），默认 📁 |

**响应示例**：
```json
{
  "success": true,
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 1,
    "name": "开发工具",
    "icon": "🔧",
    "bookmarkCount": 0,
    "sortOrder": 0,
    "createdAt": "2026-01-06T10:00:00"
  }
}
```

---

### 3. 更新分类

**接口地址**：`PUT /categories/{id}`

**请求体**：
```json
{
  "name": "开发工具集合",
  "icon": "⚙️"
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

### 4. 删除分类

**接口地址**：`DELETE /categories/{id}`

**请求参数**（Query）：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| moveBookmarksTo | Long | 否 | 将该分类下的书签移动到的目标分类ID，不传则设为未分类 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 🔄 排序接口

> ⚠️ 以下接口均需要在请求头中携带 Token

### 1. 调整分类顺序

**接口地址**：`PUT /categories/reorder`

**请求体**：
```json
{
  "categoryIds": [3, 1, 2, 5, 4]
}
```

**说明**：categoryIds 数组按新顺序排列，索引位置即为 sortOrder 值。

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "排序更新成功",
  "data": null
}
```

---

### 2. 调整书签顺序

**接口地址**：`PUT /bookmarks/reorder`

**请求体**：
```json
{
  "bookmarkIds": [5, 3, 1, 2, 4],
  "categoryId": 1
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| bookmarkIds | Array | 是 | 按新顺序排列的书签ID数组 |
| categoryId | Long | 否 | 分类ID，用于限定排序范围 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "排序更新成功",
  "data": null
}
```

---

### 3. 移动书签到分类

**接口地址**：`PUT /bookmarks/{id}/move`

**请求体**：
```json
{
  "targetCategoryId": 2
}
```

**请求参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| targetCategoryId | Long | 否 | 目标分类ID，null 表示移动到未分类 |

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "书签已移动",
  "data": {
    "id": 1,
    "title": "GitHub",
    "categoryId": 2,
    "categoryName": "学习资源"
  }
}
```

---

## 📊 数据管理接口

> ⚠️ 以下接口均需要在请求头中携带 Token

### 1. 导出书签数据

**接口地址**：`GET /auth/export`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "导出成功",
  "data": {
    "exportTime": "2026-01-06T15:00:00",
    "bookmarks": [
      {
        "id": 1,
        "title": "GitHub",
        "url": "https://github.com",
        "description": "代码托管平台",
        "categoryId": 1,
        "categoryName": "开发工具"
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "开发工具",
        "icon": "🔧"
      }
    ]
  }
}
```

---

### 2. 导入书签数据

**接口地址**：`POST /auth/import`

**请求体**：
```json
{
  "bookmarks": [
    {
      "title": "GitHub",
      "url": "https://github.com",
      "description": "代码托管平台",
      "categoryId": 1
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "开发工具",
      "icon": "🔧"
    }
  ]
}
```

**导入逻辑说明**：

1. **分类处理**：
   - 如果分类名称已存在，则复用已有分类
   - 如果分类名称不存在，则创建新分类
   - 旧分类ID会自动映射到新分类ID

2. **书签处理**：
   - 如果书签URL已存在，则跳过该书签
   - 书签的 categoryId 会自动映射到新分类ID

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "导入成功",
  "data": {
    "importedBookmarks": 15,
    "importedCategories": 3
  }
}
```

---

### 3. 清空所有数据

**接口地址**：`DELETE /auth/data/clear`

**响应示例**：
```json
{
  "success": true,
  "code": 200,
  "message": "数据已清空",
  "data": {
    "deletedBookmarks": 50,
    "deletedCategories": 5
  }
}
```

> **警告**：此操作将删除用户的所有书签和分类，无法恢复！

---

## 📦 数据模型

### User（用户实体）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键ID |
| username | String | 用户名 |
| password | String | 密码（BCrypt加密） |
| email | String | 邮箱 |
| avatar | String | 头像（emoji） |
| createdAt | DateTime | 创建时间 |

### Bookmark（书签实体）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键ID |
| userId | Long | 用户ID（外键） |
| title | String | 书签标题 |
| url | String | 网址 |
| description | String | 描述 |
| favicon | String | 网站图标URL（自动生成） |
| categoryId | Long | 分类ID（外键，可为null） |
| sortOrder | Integer | 排序顺序（数值越小越靠前） |
| createdAt | DateTime | 创建时间 |
| updatedAt | DateTime | 更新时间 |

### Category（分类实体）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键ID |
| userId | Long | 用户ID（外键） |
| name | String | 分类名称 |
| icon | String | 分类图标（emoji） |
| sortOrder | Integer | 排序顺序（数值越小越靠前） |
| createdAt | DateTime | 创建时间 |

### UserSettings（用户设置实体）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | Long | - | 主键ID |
| userId | Long | - | 用户ID（外键，唯一） |
| theme | String | "light" | 主题模式 (light/dark) |
| defaultView | String | "grid" | 默认视图 (grid/list) |

---

## 🗃️ 数据库设计

### 创建数据库

```sql
-- 创建数据库（使用 UTF-8 编码）
CREATE DATABASE IF NOT EXISTS bookmark_hub 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE bookmark_hub;
```

### users 表

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    avatar VARCHAR(10) DEFAULT '😀',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### bookmarks 表

```sql
CREATE TABLE bookmarks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description VARCHAR(500),
    favicon VARCHAR(500),
    category_id BIGINT,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### categories 表

```sql
CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    icon VARCHAR(10) DEFAULT '📁',
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### user_settings 表

```sql
CREATE TABLE user_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    theme VARCHAR(10) DEFAULT 'light',
    default_view VARCHAR(10) DEFAULT 'grid',
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 📝 更新记录

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-01-06 | v1.0 | 初始版本，包含书签和分类的CRUD接口 |
| 2026-01-06 | v1.1 | 新增排序接口（分类排序、书签排序、跨分类移动）|
| 2026-01-06 | v2.0 | 完善后端实现，新增注销账户、数据导入导出、清空数据接口 |

---

## ⚠️ 注意事项

1. **CORS 跨域**：后端已配置允许 `http://localhost:*` 和 `http://127.0.0.1:*` 访问
2. **Token 有效期**：JWT Token 有效期为 24 小时
3. **密码安全**：密码使用 BCrypt 加密存储
4. **数据隔离**：用户只能操作自己的书签和分类
5. **Favicon 生成**：使用 Google Favicon API 自动获取网站图标
6. **导入去重**：导入时会跳过 URL 已存在的书签
7. **删除关联**：删除分类时，可选择将书签移动到其他分类或设为未分类

