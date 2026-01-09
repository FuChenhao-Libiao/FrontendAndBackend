package com.bookmarkmanager.dto.bookmark;

import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

/**
 * 书签排序请求
 */
@Data
public class BookmarkReorderRequest {

    @NotEmpty(message = "书签ID列表不能为空")
    private List<Long> bookmarkIds;

    private Long categoryId;
}
