package com.bookmarkmanager.dto.bookmark;

import lombok.Data;

/**
 * 移动书签到分类请求
 */
@Data
public class BookmarkMoveRequest {

    private Long targetCategoryId;
}
