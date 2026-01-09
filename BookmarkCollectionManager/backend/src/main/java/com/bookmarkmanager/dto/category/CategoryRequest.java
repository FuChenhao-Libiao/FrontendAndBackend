package com.bookmarkmanager.dto.category;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 创建/更新分类请求
 */
@Data
public class CategoryRequest {

    @NotBlank(message = "分类名称不能为空")
    @Size(max = 50, message = "分类名称最多50个字符")
    private String name;

    @Size(max = 10, message = "图标最多10个字符")
    private String icon;
}
