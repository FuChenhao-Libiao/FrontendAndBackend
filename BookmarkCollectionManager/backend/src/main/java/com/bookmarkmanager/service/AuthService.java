package com.bookmarkmanager.service;

import com.bookmarkmanager.dto.auth.*;
import com.bookmarkmanager.entity.Bookmark;
import com.bookmarkmanager.entity.Category;
import com.bookmarkmanager.entity.User;
import com.bookmarkmanager.entity.UserSettings;
import com.bookmarkmanager.exception.BusinessException;
import com.bookmarkmanager.repository.BookmarkRepository;
import com.bookmarkmanager.repository.CategoryRepository;
import com.bookmarkmanager.repository.UserRepository;
import com.bookmarkmanager.repository.UserSettingsRepository;
import com.bookmarkmanager.security.JwtUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 用户认证服务
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final UserSettingsRepository userSettingsRepository;
    private final CategoryRepository categoryRepository;
    private final BookmarkRepository bookmarkRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    /**
     * 用户注册
     */
    @Transactional
    public UserResponse register(RegisterRequest request) {
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new BusinessException("用户名已被注册");
        }

        // 检查邮箱是否已存在
        if (request.getEmail() != null && !request.getEmail().isEmpty() 
            && userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("邮箱已被使用");
        }

        // 创建用户
        User user = User.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .email(request.getEmail())
                .avatar("😊")
                .build();
        
        user = userRepository.save(user);

        // 创建默认设置
        UserSettings settings = UserSettings.builder()
                .userId(user.getId())
                .theme("light")
                .defaultView("grid")
                .build();
        userSettingsRepository.save(settings);

        // 创建默认分类和书签
        createDefaultCategoriesAndBookmarks(user.getId());

        return toUserResponse(user);
    }

    /**
     * 创建默认分类和书签
     */
    private void createDefaultCategoriesAndBookmarks(Long userId) {
        // 创建默认分类
        Category techCategory = categoryRepository.save(Category.builder()
                .userId(userId)
                .name("技术开发")
                .icon("💻")
                .sortOrder(1)
                .build());

        Category toolsCategory = categoryRepository.save(Category.builder()
                .userId(userId)
                .name("常用工具")
                .icon("🔧")
                .sortOrder(2)
                .build());

        Category studyCategory = categoryRepository.save(Category.builder()
                .userId(userId)
                .name("学习资源")
                .icon("📚")
                .sortOrder(3)
                .build());

        Category entertainCategory = categoryRepository.save(Category.builder()
                .userId(userId)
                .name("休闲娱乐")
                .icon("🎮")
                .sortOrder(4)
                .build());

        // 创建默认书签 - 技术开发
        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("GitHub")
                .url("https://github.com")
                .description("全球最大的代码托管平台")
                .categoryId(techCategory.getId())
                .sortOrder(1)
                .build());

        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("Stack Overflow")
                .url("https://stackoverflow.com")
                .description("程序员问答社区")
                .categoryId(techCategory.getId())
                .sortOrder(2)
                .build());

        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("MDN Web Docs")
                .url("https://developer.mozilla.org")
                .description("Web开发权威文档")
                .categoryId(techCategory.getId())
                .sortOrder(3)
                .build());

        // 创建默认书签 - 常用工具
        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("Google")
                .url("https://www.google.com")
                .description("全球最大的搜索引擎")
                .categoryId(toolsCategory.getId())
                .sortOrder(1)
                .build());

        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("百度翻译")
                .url("https://fanyi.baidu.com")
                .description("在线翻译工具")
                .categoryId(toolsCategory.getId())
                .sortOrder(2)
                .build());

        // 创建默认书签 - 学习资源
        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("菜鸟教程")
                .url("https://www.runoob.com")
                .description("编程入门学习网站")
                .categoryId(studyCategory.getId())
                .sortOrder(1)
                .build());

        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("Bilibili")
                .url("https://www.bilibili.com")
                .description("学习视频平台")
                .categoryId(studyCategory.getId())
                .sortOrder(2)
                .build());

        // 创建默认书签 - 休闲娱乐
        bookmarkRepository.save(Bookmark.builder()
                .userId(userId)
                .title("豆瓣")
                .url("https://www.douban.com")
                .description("电影、书籍、音乐评分")
                .categoryId(entertainCategory.getId())
                .sortOrder(1)
                .build());
    }

    /**
     * 用户登录
     */
    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new BusinessException(401, "用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(401, "用户名或密码错误");
        }

        String token = jwtUtils.generateToken(user.getId(), user.getUsername());

        return LoginResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .avatar(user.getAvatar())
                .token(token)
                .expiresIn(jwtUtils.getExpirationTime())
                .createdAt(user.getCreatedAt())
                .build();
    }

    /**
     * 获取当前用户信息
     */
    public UserResponse getCurrentUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(404, "用户不存在"));
        return toUserResponse(user);
    }

    /**
     * 修改密码
     */
    @Transactional
    public void changePassword(Long userId, ChangePasswordRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(404, "用户不存在"));

        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
            throw new BusinessException("当前密码不正确");
        }

        if (request.getCurrentPassword().equals(request.getNewPassword())) {
            throw new BusinessException("新密码不能与当前密码相同");
        }

        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        userRepository.save(user);
    }

    /**
     * 更新用户信息
     */
    @Transactional
    public UserResponse updateProfile(Long userId, UpdateProfileRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(404, "用户不存在"));

        // 更新用户名
        if (request.getUsername() != null && !request.getUsername().equals(user.getUsername())) {
            if (userRepository.existsByUsername(request.getUsername())) {
                throw new BusinessException("用户名已被使用");
            }
            user.setUsername(request.getUsername());
        }

        // 更新邮箱
        if (request.getEmail() != null) {
            if (!request.getEmail().equals(user.getEmail()) 
                && userRepository.existsByEmail(request.getEmail())) {
                throw new BusinessException("邮箱已被使用");
            }
            user.setEmail(request.getEmail());
        }

        // 更新头像
        if (request.getAvatar() != null) {
            user.setAvatar(request.getAvatar());
        }

        user = userRepository.save(user);
        return toUserResponse(user);
    }

    /**
     * 获取用户设置
     */
    public UserSettingsDTO getSettings(Long userId) {
        UserSettings settings = userSettingsRepository.findByUserId(userId)
                .orElseGet(() -> {
                    // 如果不存在，创建默认设置
                    UserSettings newSettings = UserSettings.builder()
                            .userId(userId)
                            .theme("light")
                            .defaultView("grid")
                            .build();
                    return userSettingsRepository.save(newSettings);
                });

        UserSettingsDTO dto = new UserSettingsDTO();
        dto.setTheme(settings.getTheme());
        dto.setDefaultView(settings.getDefaultView());
        return dto;
    }

    /**
     * 更新用户设置
     */
    @Transactional
    public UserSettingsDTO updateSettings(Long userId, UserSettingsDTO request) {
        UserSettings settings = userSettingsRepository.findByUserId(userId)
                .orElseGet(() -> UserSettings.builder().userId(userId).build());

        if (request.getTheme() != null) {
            settings.setTheme(request.getTheme());
        }
        if (request.getDefaultView() != null) {
            settings.setDefaultView(request.getDefaultView());
        }

        settings = userSettingsRepository.save(settings);

        UserSettingsDTO dto = new UserSettingsDTO();
        dto.setTheme(settings.getTheme());
        dto.setDefaultView(settings.getDefaultView());
        return dto;
    }

    /**
     * 注销账户
     */
    @Transactional
    public void deleteAccount(Long userId, String password) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(404, "用户不存在"));

        // 验证密码
        if (password == null || !passwordEncoder.matches(password, user.getPassword())) {
            throw new BusinessException("密码不正确");
        }

        // 删除用户的所有数据
        // 1. 删除书签
        bookmarkRepository.deleteAllByUserId(userId);
        // 2. 删除分类
        categoryRepository.deleteAllByUserId(userId);
        // 3. 删除用户设置
        userSettingsRepository.deleteByUserId(userId);
        // 4. 删除用户
        userRepository.delete(user);
    }

    private UserResponse toUserResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .avatar(user.getAvatar())
                .createdAt(user.getCreatedAt())
                .build();
    }
}
