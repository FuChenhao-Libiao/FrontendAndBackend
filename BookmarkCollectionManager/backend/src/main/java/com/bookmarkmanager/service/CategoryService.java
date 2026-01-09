package com.bookmarkmanager.service;

import com.bookmarkmanager.dto.category.CategoryRequest;
import com.bookmarkmanager.dto.category.CategoryResponse;
import com.bookmarkmanager.entity.Category;
import com.bookmarkmanager.exception.BusinessException;
import com.bookmarkmanager.repository.BookmarkRepository;
import com.bookmarkmanager.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 分类服务
 */
@Service
@RequiredArgsConstructor
public class CategoryService {

    private final CategoryRepository categoryRepository;
    private final BookmarkRepository bookmarkRepository;

    /**
     * 获取用户的所有分类
     */
    public List<CategoryResponse> getCategories(Long userId) {
        List<Category> categories = categoryRepository.findByUserIdOrderBySortOrderAsc(userId);
        return categories.stream()
                .map(this::toCategoryResponse)
                .collect(Collectors.toList());
    }

    /**
     * 创建分类
     */
    @Transactional
    public CategoryResponse createCategory(Long userId, CategoryRequest request) {
        // 检查名称是否重复
        if (categoryRepository.existsByNameAndUserId(request.getName(), userId)) {
            throw new BusinessException("分类名称已存在");
        }

        // 获取最大排序号
        Integer maxSortOrder = categoryRepository.findMaxSortOrderByUserId(userId);

        Category category = Category.builder()
                .userId(userId)
                .name(request.getName())
                .icon(request.getIcon() != null ? request.getIcon() : "📁")
                .sortOrder(maxSortOrder + 1)
                .build();

        category = categoryRepository.save(category);
        return toCategoryResponse(category);
    }

    /**
     * 更新分类
     */
    @Transactional
    public CategoryResponse updateCategory(Long userId, Long categoryId, CategoryRequest request) {
        Category category = categoryRepository.findByIdAndUserId(categoryId, userId)
                .orElseThrow(() -> new BusinessException(404, "分类不存在"));

        // 检查名称是否与其他分类重复
        if (categoryRepository.existsByNameAndUserIdAndIdNot(request.getName(), userId, categoryId)) {
            throw new BusinessException("分类名称已存在");
        }

        category.setName(request.getName());
        if (request.getIcon() != null) {
            category.setIcon(request.getIcon());
        }

        category = categoryRepository.save(category);
        return toCategoryResponse(category);
    }

    /**
     * 删除分类
     */
    @Transactional
    public void deleteCategory(Long userId, Long categoryId, Long moveBookmarksTo) {
        Category category = categoryRepository.findByIdAndUserId(categoryId, userId)
                .orElseThrow(() -> new BusinessException(404, "分类不存在"));

        // 处理该分类下的书签
        if (moveBookmarksTo != null) {
            // 移动到指定分类
            categoryRepository.findByIdAndUserId(moveBookmarksTo, userId)
                    .orElseThrow(() -> new BusinessException(404, "目标分类不存在"));
            // 这里简化处理，直接将书签的 categoryId 设为目标分类
            List<com.bookmarkmanager.entity.Bookmark> bookmarks = 
                bookmarkRepository.findByUserIdAndCategoryIdOrderBySortOrderAsc(userId, categoryId);
            bookmarks.forEach(b -> b.setCategoryId(moveBookmarksTo));
            bookmarkRepository.saveAll(bookmarks);
        } else {
            // 设为未分类
            bookmarkRepository.clearCategoryId(categoryId);
        }

        categoryRepository.delete(category);
    }

    /**
     * 调整分类顺序
     */
    @Transactional
    public void reorderCategories(Long userId, List<Long> categoryIds) {
        for (int i = 0; i < categoryIds.size(); i++) {
            Category category = categoryRepository.findByIdAndUserId(categoryIds.get(i), userId)
                    .orElseThrow(() -> new BusinessException(404, "分类不存在"));
            category.setSortOrder(i);
            categoryRepository.save(category);
        }
    }

    private CategoryResponse toCategoryResponse(Category category) {
        long bookmarkCount = bookmarkRepository.countByCategoryId(category.getId());
        return CategoryResponse.builder()
                .id(category.getId())
                .name(category.getName())
                .icon(category.getIcon())
                .bookmarkCount((int) bookmarkCount)
                .sortOrder(category.getSortOrder())
                .createdAt(category.getCreatedAt())
                .build();
    }

    /**
     * 删除用户的所有分类
     */
    @Transactional
    public int deleteAllCategoriesByUserId(Long userId) {
        List<Category> categories = categoryRepository.findByUserIdOrderBySortOrderAsc(userId);
        int count = categories.size();
        categoryRepository.deleteAll(categories);
        return count;
    }
}
