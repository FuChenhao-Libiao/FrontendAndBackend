package com.bookmarkmanager.dto.auth;

import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 更新用户信息请求
 */
@Data
public class UpdateProfileRequest {

    @Size(min = 4, max = 20, message = "用户名长度应为4-20个字符")
    private String username;

    private String avatar;

    private String email;
}
