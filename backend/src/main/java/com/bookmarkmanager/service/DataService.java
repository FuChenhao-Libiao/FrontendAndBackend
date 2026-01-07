package com.bookmarkmanager.service;

import com.bookmarkmanager.entity.Bookmark;
import com.bookmarkmanager.entity.Category;
import com.bookmarkmanager.repository.BookmarkRepository;
import com.bookmarkmanager.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 数据导入导出服务
 */
@Service
@RequiredArgsConstructor
public class DataService {

    private final BookmarkRepository bookmarkRepository;
    private final CategoryRepository categoryRepository;

    /**
     * 导入数据
     */
    @Transactional
    @SuppressWarnings("unchecked")
    public Map<String, Integer> importData(Long userId, Map<String, Object> data) {
        int importedCategories = 0;
        int importedBookmarks = 0;

        // 用于映射旧分类ID到新分类ID
        Map<Object, Long> categoryIdMapping = new HashMap<>();

        // 1. 导入分类
        List<Map<String, Object>> categories = (List<Map<String, Object>>) data.get("categories");
        if (categories != null && !categories.isEmpty()) {
            // 获取当前最大排序号
            Integer maxSortOrder = categoryRepository.findMaxSortOrderByUserId(userId);
            
            for (Map<String, Object> catData : categories) {
                String name = (String) catData.get("name");
                String icon = catData.get("icon") != null ? (String) catData.get("icon") : "📁";
                Object oldId = catData.get("id");

                // 检查是否已存在同名分类
                Category existingCategory = categoryRepository.findByNameAndUserId(name, userId);
                
                if (existingCategory != null) {
                    // 如果已存在同名分类，直接使用
                    categoryIdMapping.put(oldId, existingCategory.getId());
                } else {
                    // 创建新分类
                    maxSortOrder++;
                    Category category = Category.builder()
                            .userId(userId)
                            .name(name)
                            .icon(icon)
                            .sortOrder(maxSortOrder)
                            .build();
                    category = categoryRepository.save(category);
                    categoryIdMapping.put(oldId, category.getId());
                    importedCategories++;
                }
            }
        }

        // 2. 导入书签
        List<Map<String, Object>> bookmarks = (List<Map<String, Object>>) data.get("bookmarks");
        if (bookmarks != null && !bookmarks.isEmpty()) {
            // 获取当前最大排序号
            Integer maxSortOrder = bookmarkRepository.findMaxSortOrderByUserId(userId);
            
            for (Map<String, Object> bookmarkData : bookmarks) {
                String title = (String) bookmarkData.get("title");
                String url = (String) bookmarkData.get("url");
                String description = bookmarkData.get("description") != null ? 
                        (String) bookmarkData.get("description") : "";
                
                // 检查是否已存在相同URL的书签
                if (bookmarkRepository.existsByUrlAndUserId(url, userId)) {
                    continue; // 跳过重复的书签
                }

                // 获取分类ID
                Long categoryId = null;
                Object oldCategoryId = bookmarkData.get("categoryId");
                if (oldCategoryId != null) {
                    categoryId = categoryIdMapping.get(oldCategoryId);
                    // 如果通过旧ID映射找不到，尝试直接使用（如果是数字）
                    if (categoryId == null && oldCategoryId instanceof Number) {
                        Long directCategoryId = ((Number) oldCategoryId).longValue();
                        // 检查该分类是否属于当前用户
                        if (categoryRepository.findByIdAndUserId(directCategoryId, userId).isPresent()) {
                            categoryId = directCategoryId;
                        }
                    }
                }

                // 生成 favicon URL
                String favicon = generateFaviconUrl(url);

                maxSortOrder++;
                Bookmark bookmark = Bookmark.builder()
                        .userId(userId)
                        .title(title)
                        .url(url)
                        .description(description)
                        .favicon(favicon)
                        .categoryId(categoryId)
                        .sortOrder(maxSortOrder)
                        .build();
                
                bookmarkRepository.save(bookmark);
                importedBookmarks++;
            }
        }

        Map<String, Integer> result = new HashMap<>();
        result.put("importedBookmarks", importedBookmarks);
        result.put("importedCategories", importedCategories);
        return result;
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
}
