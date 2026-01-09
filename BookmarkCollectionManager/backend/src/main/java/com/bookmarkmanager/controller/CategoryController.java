package com.bookmarkmanager.controller;

import com.bookmarkmanager.dto.ApiResponse;
import com.bookmarkmanager.dto.category.CategoryReorderRequest;
import com.bookmarkmanager.dto.category.CategoryRequest;
import com.bookmarkmanager.dto.category.CategoryResponse;
import com.bookmarkmanager.service.CategoryService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 分类控制器
 */
@RestController
@RequestMapping("/api/categories")
@RequiredArgsConstructor
public class CategoryController {

    private final CategoryService categoryService;

    /**
     * 获取分类列表
     */
    @GetMapping
    public ResponseEntity<ApiResponse<List<CategoryResponse>>> getCategories(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        List<CategoryResponse> categories = categoryService.getCategories(userId);
        return ResponseEntity.ok(ApiResponse.success("查询成功", categories));
    }

    /**
     * 创建分类
     */
    @PostMapping
    public ResponseEntity<ApiResponse<CategoryResponse>> createCategory(
            Authentication authentication,
            @Valid @RequestBody CategoryRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        CategoryResponse category = categoryService.createCategory(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("创建成功", category));
    }

    /**
     * 更新分类
     */
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<CategoryResponse>> updateCategory(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody CategoryRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        CategoryResponse category = categoryService.updateCategory(userId, id, request);
        return ResponseEntity.ok(ApiResponse.success("更新成功", category));
    }

    /**
     * 删除分类
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteCategory(
            Authentication authentication,
            @PathVariable Long id,
            @RequestParam(required = false) Long moveBookmarksTo) {
        Long userId = (Long) authentication.getPrincipal();
        categoryService.deleteCategory(userId, id, moveBookmarksTo);
        return ResponseEntity.ok(ApiResponse.success("删除成功", null));
    }

    /**
     * 调整分类顺序
     */
    @PutMapping("/reorder")
    public ResponseEntity<ApiResponse<Void>> reorderCategories(
            Authentication authentication,
            @Valid @RequestBody CategoryReorderRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        categoryService.reorderCategories(userId, request.getCategoryIds());
        return ResponseEntity.ok(ApiResponse.success("排序更新成功", null));
    }
}
