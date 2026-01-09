package com.bookmarkmanager.service;

import com.bookmarkmanager.dto.bookmark.*;
import com.bookmarkmanager.entity.Bookmark;
import com.bookmarkmanager.entity.Category;
import com.bookmarkmanager.exception.BusinessException;
import com.bookmarkmanager.repository.BookmarkRepository;
import com.bookmarkmanager.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 书签服务
 */
@Service
@RequiredArgsConstructor
public class BookmarkService {

    private final BookmarkRepository bookmarkRepository;
    private final CategoryRepository categoryRepository;

    /**
     * 获取书签列表（分页）
     */
    public PageResponse<BookmarkResponse> getBookmarks(Long userId, Integer page, Integer size, 
                                                        Long categoryId, String keyword) {
        Pageable pageable = PageRequest.of(page - 1, size);
        Page<Bookmark> bookmarkPage;

        if (keyword != null && !keyword.trim().isEmpty()) {
            if (categoryId != null) {
                bookmarkPage = bookmarkRepository.searchByCategoryAndKeyword(userId, categoryId, keyword, pageable);
            } else {
                bookmarkPage = bookmarkRepository.searchByKeyword(userId, keyword, pageable);
            }
        } else if (categoryId != null) {
            bookmarkPage = bookmarkRepository.findByUserIdAndCategoryIdOrderBySortOrderAsc(userId, categoryId, pageable);
        } else {
            bookmarkPage = bookmarkRepository.findByUserIdOrderBySortOrderAsc(userId, pageable);
        }

        List<BookmarkResponse> list = bookmarkPage.getContent().stream()
                .map(this::toBookmarkResponse)
                .collect(Collectors.toList());

        return PageResponse.<BookmarkResponse>builder()
                .total(bookmarkPage.getTotalElements())
                .page(page)
                .size(size)
                .list(list)
                .build();
    }

    /**
     * 获取单个书签
     */
    public BookmarkResponse getBookmark(Long userId, Long bookmarkId) {
        Bookmark bookmark = bookmarkRepository.findByIdAndUserId(bookmarkId, userId)
                .orElseThrow(() -> new BusinessException(404, "书签不存在"));
        return toBookmarkResponse(bookmark);
    }

    /**
     * 创建书签
     */
    @Transactional
    public BookmarkResponse createBookmark(Long userId, BookmarkRequest request) {
        // 验证分类是否存在
        if (request.getCategoryId() != null) {
            categoryRepository.findByIdAndUserId(request.getCategoryId(), userId)
                    .orElseThrow(() -> new BusinessException(404, "分类不存在"));
        }

        // 获取最大排序号
        Integer maxSortOrder = bookmarkRepository.findMaxSortOrderByUserId(userId);

        // 生成 favicon URL
        String favicon = generateFaviconUrl(request.getUrl());

        Bookmark bookmark = Bookmark.builder()
                .userId(userId)
                .title(request.getTitle())
                .url(request.getUrl())
                .description(request.getDescription())
                .favicon(favicon)
                .categoryId(request.getCategoryId())
                .sortOrder(maxSortOrder + 1)
                .build();

        bookmark = bookmarkRepository.save(bookmark);
        return toBookmarkResponse(bookmark);
    }

    /**
     * 更新书签
     */
    @Transactional
    public BookmarkResponse updateBookmark(Long userId, Long bookmarkId, BookmarkRequest request) {
        Bookmark bookmark = bookmarkRepository.findByIdAndUserId(bookmarkId, userId)
                .orElseThrow(() -> new BusinessException(404, "书签不存在"));

        // 验证分类是否存在
        if (request.getCategoryId() != null) {
            categoryRepository.findByIdAndUserId(request.getCategoryId(), userId)
                    .orElseThrow(() -> new BusinessException(404, "分类不存在"));
        }

        bookmark.setTitle(request.getTitle());
        bookmark.setUrl(request.getUrl());
        bookmark.setDescription(request.getDescription());
        bookmark.setCategoryId(request.getCategoryId());
        
        // 如果 URL 变了，更新 favicon
        if (!bookmark.getUrl().equals(request.getUrl())) {
            bookmark.setFavicon(generateFaviconUrl(request.getUrl()));
        }

        bookmark = bookmarkRepository.save(bookmark);
        return toBookmarkResponse(bookmark);
    }

    /**
     * 删除书签
     */
    @Transactional
    public void deleteBookmark(Long userId, Long bookmarkId) {
        Bookmark bookmark = bookmarkRepository.findByIdAndUserId(bookmarkId, userId)
                .orElseThrow(() -> new BusinessException(404, "书签不存在"));
        bookmarkRepository.delete(bookmark);
    }

    /**
     * 批量删除书签
     */
    @Transactional
    public int batchDeleteBookmarks(Long userId, List<Long> ids) {
        bookmarkRepository.deleteByIdsAndUserId(ids, userId);
        return ids.size();
    }

    /**
     * 调整书签顺序
     */
    @Transactional
    public void reorderBookmarks(Long userId, List<Long> bookmarkIds, Long categoryId) {
        for (int i = 0; i < bookmarkIds.size(); i++) {
            Bookmark bookmark = bookmarkRepository.findByIdAndUserId(bookmarkIds.get(i), userId)
                    .orElseThrow(() -> new BusinessException(404, "书签不存在"));
            bookmark.setSortOrder(i);
            bookmarkRepository.save(bookmark);
        }
    }

    /**
     * 移动书签到分类
     */
    @Transactional
    public BookmarkResponse moveBookmark(Long userId, Long bookmarkId, Long targetCategoryId) {
        Bookmark bookmark = bookmarkRepository.findByIdAndUserId(bookmarkId, userId)
                .orElseThrow(() -> new BusinessException(404, "书签不存在"));

        // 验证目标分类
        if (targetCategoryId != null) {
            categoryRepository.findByIdAndUserId(targetCategoryId, userId)
                    .orElseThrow(() -> new BusinessException(404, "目标分类不存在"));
        }

        bookmark.setCategoryId(targetCategoryId);
        bookmark = bookmarkRepository.save(bookmark);
        return toBookmarkResponse(bookmark);
    }

    /**
     * 获取用户的所有书签（用于导出）
     */
    public List<BookmarkResponse> getAllBookmarks(Long userId) {
        return bookmarkRepository.findByUserIdOrderBySortOrderAsc(userId).stream()
                .map(this::toBookmarkResponse)
                .collect(Collectors.toList());
    }

    /**
     * 获取用户书签数量
     */
    public long getBookmarkCount(Long userId) {
        return bookmarkRepository.countByUserId(userId);
    }

    private BookmarkResponse toBookmarkResponse(Bookmark bookmark) {
        String categoryName = null;
        if (bookmark.getCategoryId() != null) {
            categoryName = categoryRepository.findById(bookmark.getCategoryId())
                    .map(Category::getName)
                    .orElse(null);
        }

        return BookmarkResponse.builder()
                .id(bookmark.getId())
                .title(bookmark.getTitle())
                .url(bookmark.getUrl())
                .description(bookmark.getDescription())
                .favicon(bookmark.getFavicon())
                .categoryId(bookmark.getCategoryId())
                .categoryName(categoryName)
                .sortOrder(bookmark.getSortOrder())
                .createdAt(bookmark.getCreatedAt())
                .updatedAt(bookmark.getUpdatedAt())
                .build();
    }

    private String generateFaviconUrl(String url) {
        try {
            java.net.URL parsedUrl = new java.net.URL(url);
            String domain = parsedUrl.getHost();
            return "https://www.google.com/s2/favicons?domain=" + domain + "&sz=64";
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 删除用户的所有书签
     */
    @Transactional
    public int deleteAllBookmarksByUserId(Long userId) {
        List<Bookmark> bookmarks = bookmarkRepository.findByUserIdOrderBySortOrderAsc(userId, null).getContent();
        int count = bookmarks.size();
        bookmarkRepository.deleteAll(bookmarks);
        return count;
    }
}
