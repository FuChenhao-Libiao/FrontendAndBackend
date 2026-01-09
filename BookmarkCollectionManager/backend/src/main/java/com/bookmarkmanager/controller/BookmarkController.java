package com.bookmarkmanager.controller;

import com.bookmarkmanager.dto.ApiResponse;
import com.bookmarkmanager.dto.bookmark.*;
import com.bookmarkmanager.service.BookmarkService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 书签控制器
 */
@RestController
@RequestMapping("/api/bookmarks")
@RequiredArgsConstructor
public class BookmarkController {

    private final BookmarkService bookmarkService;

    /**
     * 获取书签列表（分页）
     */
    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<BookmarkResponse>>> getBookmarks(
            Authentication authentication,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) String keyword) {
        Long userId = (Long) authentication.getPrincipal();
        PageResponse<BookmarkResponse> response = bookmarkService.getBookmarks(userId, page, size, categoryId, keyword);
        return ResponseEntity.ok(ApiResponse.success("查询成功", response));
    }

    /**
     * 获取单个书签
     */
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<BookmarkResponse>> getBookmark(
            Authentication authentication,
            @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        BookmarkResponse bookmark = bookmarkService.getBookmark(userId, id);
        return ResponseEntity.ok(ApiResponse.success("查询成功", bookmark));
    }

    /**
     * 创建书签
     */
    @PostMapping
    public ResponseEntity<ApiResponse<BookmarkResponse>> createBookmark(
            Authentication authentication,
            @Valid @RequestBody BookmarkRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        BookmarkResponse bookmark = bookmarkService.createBookmark(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("创建成功", bookmark));
    }

    /**
     * 更新书签
     */
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<BookmarkResponse>> updateBookmark(
            Authentication authentication,
            @PathVariable Long id,
            @Valid @RequestBody BookmarkRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        BookmarkResponse bookmark = bookmarkService.updateBookmark(userId, id, request);
        return ResponseEntity.ok(ApiResponse.success("更新成功", bookmark));
    }

    /**
     * 删除书签
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteBookmark(
            Authentication authentication,
            @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        bookmarkService.deleteBookmark(userId, id);
        return ResponseEntity.ok(ApiResponse.success("删除成功", null));
    }

    /**
     * 批量删除书签
     */
    @DeleteMapping("/batch")
    public ResponseEntity<ApiResponse<Map<String, Integer>>> batchDeleteBookmarks(
            Authentication authentication,
            @RequestBody Map<String, List<Long>> request) {
        Long userId = (Long) authentication.getPrincipal();
        List<Long> ids = request.get("ids");
        int deletedCount = bookmarkService.batchDeleteBookmarks(userId, ids);
        return ResponseEntity.ok(ApiResponse.success("批量删除成功", Map.of("deletedCount", deletedCount)));
    }

    /**
     * 调整书签顺序
     */
    @PutMapping("/reorder")
    public ResponseEntity<ApiResponse<Void>> reorderBookmarks(
            Authentication authentication,
            @Valid @RequestBody BookmarkReorderRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        bookmarkService.reorderBookmarks(userId, request.getBookmarkIds(), request.getCategoryId());
        return ResponseEntity.ok(ApiResponse.success("排序更新成功", null));
    }

    /**
     * 移动书签到分类
     */
    @PutMapping("/{id}/move")
    public ResponseEntity<ApiResponse<BookmarkResponse>> moveBookmark(
            Authentication authentication,
            @PathVariable Long id,
            @RequestBody BookmarkMoveRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        BookmarkResponse bookmark = bookmarkService.moveBookmark(userId, id, request.getTargetCategoryId());
        return ResponseEntity.ok(ApiResponse.success("书签已移动到目标分类", bookmark));
    }
}
