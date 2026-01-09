package com.bookmarkmanager.dto.auth;

import lombok.Data;

/**
 * 用户设置请求/响应
 */
@Data
public class UserSettingsDTO {

    private String theme;
    private String defaultView;
}
