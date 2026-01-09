package com.bookmarkmanager.service;

import com.bookmarkmanager.dto.statistics.StatisticsResponse;
import com.bookmarkmanager.entity.Bookmark;
import com.bookmarkmanager.entity.Category;
import com.bookmarkmanager.repository.BookmarkRepository;
import com.bookmarkmanager.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 统计服务
 */
@Service
@RequiredArgsConstructor
public class StatisticsService {

    private final BookmarkRepository bookmarkRepository;
    private final CategoryRepository categoryRepository;

    /**
     * 获取统计概览
     */
    public StatisticsResponse getStatistics(Long userId) {
        // 获取用户的所有书签
        List<Bookmark> bookmarks = bookmarkRepository.findByUserIdOrderBySortOrderAsc(userId);
        
        // 获取用户的所有分类
        List<Category> categories = categoryRepository.findByUserIdOrderBySortOrderAsc(userId);

        // 统计今日新增
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        long todayAdded = bookmarks.stream()
                .filter(b -> b.getCreatedAt() != null && b.getCreatedAt().isAfter(todayStart))
                .count();

        // 统计各分类书签数量
        List<StatisticsResponse.CategoryStat> categoryStats = categories.stream()
                .map(category -> {
                    long count = bookmarks.stream()
                            .filter(b -> category.getId().equals(b.getCategoryId()))
                            .count();
                    return StatisticsResponse.CategoryStat.builder()
                            .categoryId(category.getId())
                            .categoryName(category.getName())
                            .count(count)
                            .build();
                })
                .collect(Collectors.toList());

        // 添加未分类统计
        long uncategorizedCount = bookmarks.stream()
                .filter(b -> b.getCategoryId() == null)
                .count();
        if (uncategorizedCount > 0) {
            categoryStats.add(StatisticsResponse.CategoryStat.builder()
                    .categoryId(null)
                    .categoryName("未分类")
                    .count(uncategorizedCount)
                    .build());
        }

        return StatisticsResponse.builder()
                .totalBookmarks(bookmarks.size())
                .totalCategories(categories.size())
                .todayAdded(todayAdded)
                .categoryStats(categoryStats)
                .build();
    }
}
