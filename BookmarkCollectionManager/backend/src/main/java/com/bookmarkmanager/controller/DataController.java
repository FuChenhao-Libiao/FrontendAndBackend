package com.bookmarkmanager.controller;

import com.bookmarkmanager.dto.ApiResponse;
import com.bookmarkmanager.dto.bookmark.BookmarkResponse;
import com.bookmarkmanager.dto.category.CategoryResponse;
import com.bookmarkmanager.service.BookmarkService;
import com.bookmarkmanager.service.CategoryService;
import com.bookmarkmanager.service.DataService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 数据导入导出控制器
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class DataController {

    private final BookmarkService bookmarkService;
    private final CategoryService categoryService;
    private final DataService dataService;

    /**
     * 导出数据
     */
    @GetMapping("/export")
    public ResponseEntity<ApiResponse<Map<String, Object>>> exportData(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();

        List<BookmarkResponse> bookmarks = bookmarkService.getAllBookmarks(userId);
        List<CategoryResponse> categories = categoryService.getCategories(userId);

        Map<String, Object> data = new HashMap<>();
        data.put("exportTime", LocalDateTime.now());
        data.put("bookmarks", bookmarks);
        data.put("categories", categories);

        return ResponseEntity.ok(ApiResponse.success("导出成功", data));
    }

    /**
     * 导入数据
     */
    @PostMapping("/import")
    public ResponseEntity<ApiResponse<Map<String, Integer>>> importData(
            Authentication authentication,
            @RequestBody Map<String, Object> request) {
        Long userId = (Long) authentication.getPrincipal();

        // 调用 DataService 进行导入
        Map<String, Integer> result = dataService.importData(userId, request);

        return ResponseEntity.ok(ApiResponse.success("导入成功", result));
    }

    /**
     * 清空所有数据
     */
    @DeleteMapping("/data/clear")
    public ResponseEntity<ApiResponse<Map<String, Integer>>> clearAllData(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();

        // 清空书签和分类
        int deletedBookmarks = bookmarkService.deleteAllBookmarksByUserId(userId);
        int deletedCategories = categoryService.deleteAllCategoriesByUserId(userId);

        Map<String, Integer> result = new HashMap<>();
        result.put("deletedBookmarks", deletedBookmarks);
        result.put("deletedCategories", deletedCategories);

        return ResponseEntity.ok(ApiResponse.success("数据已清空", result));
    }
}
