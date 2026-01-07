package com.bookmarkmanager.dto.bookmark;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

/**
 * 创建/更新书签请求
 */
@Data
public class BookmarkRequest {

    @NotBlank(message = "标题不能为空")
    @Size(max = 100, message = "标题最多100个字符")
    private String title;

    @NotBlank(message = "网址不能为空")
    @URL(message = "网址格式不正确")
    @Size(max = 500, message = "网址最多500个字符")
    private String url;

    @Size(max = 500, message = "描述最多500个字符")
    private String description;

    private Long categoryId;
}
