package com.bookmarkmanager.controller;

import com.bookmarkmanager.dto.ApiResponse;
import com.bookmarkmanager.dto.auth.*;
import com.bookmarkmanager.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * 用户认证控制器
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public ResponseEntity<ApiResponse<UserResponse>> register(@Valid @RequestBody RegisterRequest request) {
        UserResponse user = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("注册成功", user));
    }

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponse>> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success("登录成功", response));
    }

    /**
     * 用户登出
     */
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout() {
        // JWT 是无状态的，客户端删除 token 即可
        return ResponseEntity.ok(ApiResponse.success("登出成功", null));
    }

    /**
     * 获取当前用户信息
     */
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserResponse>> getCurrentUser(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        UserResponse user = authService.getCurrentUser(userId);
        return ResponseEntity.ok(ApiResponse.success("查询成功", user));
    }

    /**
     * 修改密码
     */
    @PutMapping("/password")
    public ResponseEntity<ApiResponse<Void>> changePassword(
            Authentication authentication,
            @Valid @RequestBody ChangePasswordRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        authService.changePassword(userId, request);
        return ResponseEntity.ok(ApiResponse.success("密码修改成功", null));
    }

    /**
     * 更新用户信息
     */
    @PutMapping("/profile")
    public ResponseEntity<ApiResponse<UserResponse>> updateProfile(
            Authentication authentication,
            @Valid @RequestBody UpdateProfileRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        UserResponse user = authService.updateProfile(userId, request);
        return ResponseEntity.ok(ApiResponse.success("信息更新成功", user));
    }

    /**
     * 获取用户设置
     */
    @GetMapping("/settings")
    public ResponseEntity<ApiResponse<UserSettingsDTO>> getSettings(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        UserSettingsDTO settings = authService.getSettings(userId);
        return ResponseEntity.ok(ApiResponse.success("查询成功", settings));
    }

    /**
     * 更新用户设置
     */
    @PutMapping("/settings")
    public ResponseEntity<ApiResponse<UserSettingsDTO>> updateSettings(
            Authentication authentication,
            @RequestBody UserSettingsDTO request) {
        Long userId = (Long) authentication.getPrincipal();
        UserSettingsDTO settings = authService.updateSettings(userId, request);
        return ResponseEntity.ok(ApiResponse.success("设置已保存", settings));
    }

    /**
     * 注销账户
     */
    @DeleteMapping("/account")
    public ResponseEntity<ApiResponse<Void>> deleteAccount(
            Authentication authentication,
            @RequestBody java.util.Map<String, String> request) {
        Long userId = (Long) authentication.getPrincipal();
        String password = request.get("password");
        authService.deleteAccount(userId, password);
        return ResponseEntity.ok(ApiResponse.success("账户已注销", null));
    }
}
