package com.bookmarkmanager.dto.category;

import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

/**
 * 分类排序请求
 */
@Data
public class CategoryReorderRequest {

    @NotEmpty(message = "分类ID列表不能为空")
    private List<Long> categoryIds;
}
