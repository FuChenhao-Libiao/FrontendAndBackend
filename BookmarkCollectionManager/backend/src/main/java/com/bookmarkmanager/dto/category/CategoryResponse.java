package com.bookmarkmanager.dto.category;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 分类响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CategoryResponse {

    private Long id;
    private String name;
    private String icon;
    private Integer bookmarkCount;
    private Integer sortOrder;
    private LocalDateTime createdAt;
}
