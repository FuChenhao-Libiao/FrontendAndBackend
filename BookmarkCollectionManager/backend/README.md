# 📚 书签管理器后端

基于 Spring Boot 3.x 的个人书签收藏管理器后端服务，提供完整的用户认证、书签管理、分类管理和数据统计功能。

## ✨ 功能特性

- 🔐 用户认证：注册、登录、登出、密码修改
- 📑 书签管理：增删改查、批量操作、排序、分类移动
- 📁 分类管理：多级分类、自定义排序
- 📊 数据统计：书签数量、分类统计、使用分析
- 💾 数据备份：导入导出用户数据
- ⚙️ 用户设置：个性化配置

## 🛠️ 技术栈

| 类型 | 技术 | 版本 |
|------|------|------|
| **框架** | Spring Boot | 3.2.1 |
| **安全** | Spring Security + JWT | jjwt 0.12.3 |
| **持久层** | Spring Data JPA | - |
| **数据库** | MySQL | 8.x |
| **工具** | Lombok | 1.18.30 |
| **构建** | Maven | 3.8+ |
| **JDK** | Java | 17+ |

## 📁 项目结构

```
src/main/java/com/bookmarkmanager/
├── BookmarkManagerApplication.java  # 应用启动类
├── config/                          # 配置层
│   ├── CorsConfig.java              # 跨域配置
│   └── SecurityConfig.java          # Spring Security 配置
├── controller/                      # 控制器层
│   ├── AuthController.java          # 用户认证接口
│   ├── BookmarkController.java      # 书签管理接口
│   ├── CategoryController.java      # 分类管理接口
│   ├── DataController.java          # 数据导入导出接口
│   └── StatisticsController.java    # 统计数据接口
├── dto/                             # 数据传输对象
│   ├── ApiResponse.java             # 统一响应封装
│   ├── auth/                        # 认证相关 DTO
│   ├── bookmark/                    # 书签相关 DTO
│   ├── category/                    # 分类相关 DTO
│   └── statistics/                  # 统计相关 DTO
├── entity/                          # 实体类
│   ├── User.java                    # 用户实体
│   ├── Bookmark.java                # 书签实体
│   ├── Category.java                # 分类实体
│   └── UserSettings.java            # 用户设置实体
├── exception/                       # 异常处理
│   ├── BusinessException.java       # 自定义业务异常
│   └── GlobalExceptionHandler.java  # 全局异常处理器
├── repository/                      # 数据访问层
│   ├── BookmarkRepository.java
│   ├── CategoryRepository.java
│   ├── UserRepository.java
│   └── UserSettingsRepository.java
├── security/                        # 安全模块
│   ├── JwtAuthenticationFilter.java # JWT 认证过滤器
│   └── JwtUtils.java                # JWT 工具类
└── service/                         # 服务层
    ├── AuthService.java             # 认证服务
    ├── BookmarkService.java         # 书签服务
    ├── CategoryService.java         # 分类服务
    ├── DataService.java             # 数据导入导出服务
    └── StatisticsService.java       # 统计服务
```

## 🚀 快速开始

### 环境要求

- JDK 17 或更高版本
- Maven 3.8+
- MySQL 8.x

### 方式一：使用 Maven 运行（开发环境）

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **配置数据库**
   
   编辑 `src/main/resources/application.properties`，修改数据库连接信息：
   ```properties
   spring.datasource.url=jdbc:mysql://localhost:3306/bookmark_hub?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
   spring.datasource.username=root
   spring.datasource.password=root
   ```

3. **创建数据库**
   ```sql
   CREATE DATABASE bookmark_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. **运行项目**
   ```bash
   mvn spring-boot:run
   ```

5. **验证启动**
   - API 地址：http://localhost:8080/api

### 方式二：使用 JAR 包运行（生产环境）

1. **构建项目**
   ```bash
   mvn clean package -DskipTests
   ```

2. **运行 JAR 包**
   ```bash
   java -jar target/bookmark-manager-1.0.0.jar
   ```

3. **或使用启动脚本**
   
   双击 `启动书签管理器.bat` 即可启动服务。

## 📡 API 接口

### 认证接口 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:----:|
| POST | `/register` | 用户注册 | ❌ |
| POST | `/login` | 用户登录 | ❌ |
| POST | `/logout` | 用户登出 | ✅ |
| GET | `/me` | 获取当前用户信息 | ✅ |
| PUT | `/password` | 修改密码 | ✅ |
| PUT | `/profile` | 更新用户资料 | ✅ |
| GET | `/settings` | 获取用户设置 | ✅ |
| PUT | `/settings` | 更新用户设置 | ✅ |
| GET | `/export` | 导出用户数据 | ✅ |
| POST | `/import` | 导入用户数据 | ✅ |
| DELETE | `/data/clear` | 清空用户数据 | ✅ |

### 书签接口 `/api/bookmarks`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取书签列表（支持分页、筛选） |
| GET | `/{id}` | 获取单个书签详情 |
| POST | `/` | 创建书签 |
| PUT | `/{id}` | 更新书签 |
| DELETE | `/{id}` | 删除书签 |
| DELETE | `/batch` | 批量删除书签 |
| PUT | `/reorder` | 调整书签顺序 |
| PUT | `/{id}/move` | 移动书签到指定分类 |

### 分类接口 `/api/categories`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取分类列表 |
| POST | `/` | 创建分类 |
| PUT | `/{id}` | 更新分类 |
| DELETE | `/{id}` | 删除分类 |
| PUT | `/reorder` | 调整分类顺序 |

### 统计接口 `/api/statistics`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取统计概览（书签数、分类数等） |

## 📝 请求示例

### 用户注册

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "123456",
    "email": "demo@example.com"
  }'
```

### 用户登录

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "123456"
  }'
```

**响应示例：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "demo",
      "email": "demo@example.com"
    }
  }
}
```

### 获取书签列表

```bash
curl http://localhost:8080/api/bookmarks \
  -H "Authorization: Bearer <your_token>"
```

### 创建书签

```bash
curl -X POST http://localhost:8080/api/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "GitHub",
    "url": "https://github.com",
    "description": "代码托管平台",
    "categoryId": 1
  }'
```

## ⚙️ 配置说明

### application.properties

```properties
# 服务端口
server.port=8080

# 数据库配置
spring.datasource.url=jdbc:mysql://localhost:3306/bookmark_hub
spring.datasource.username=root
spring.datasource.password=root

# JPA 配置
spring.jpa.hibernate.ddl-auto=update  # 自动更新表结构

# JWT 配置
jwt.secret=YourSecretKey              # JWT 密钥（生产环境请修改）
jwt.expiration=86400000               # Token 有效期（毫秒，默认24小时）
```

### 生产环境配置

使用 `application-prod.properties` 配置生产环境参数，启动时指定 profile：

```bash
java -jar bookmark-manager-1.0.0.jar --spring.profiles.active=prod
```

## 🔒 安全说明

- 密码使用 **BCrypt** 算法加密存储
- 基于 **JWT** 实现无状态认证
- Token 有效期默认 **24 小时**
- 除登录注册外，所有接口需携带 `Authorization: Bearer <token>` 请求头
- 生产环境请务必修改 JWT 密钥

## 📂 相关文件

| 文件 | 说明 |
|------|------|
| `启动书签管理器.bat` | Windows 一键启动脚本 |
| `run.bat` | 开发环境运行脚本 |
| `pom.xml` | Maven 项目配置 |
| `application.properties` | 开发环境配置 |
| `application-prod.properties` | 生产环境配置 |

## 📄 License

MIT License
