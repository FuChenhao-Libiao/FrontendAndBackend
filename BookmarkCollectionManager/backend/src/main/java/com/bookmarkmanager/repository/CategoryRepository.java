package com.bookmarkmanager.repository;

import com.bookmarkmanager.entity.Category;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 分类数据访问层
 */
@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {

    List<Category> findByUserIdOrderBySortOrderAsc(Long userId);

    Optional<Category> findByIdAndUserId(Long id, Long userId);

    boolean existsByNameAndUserId(String name, Long userId);

    boolean existsByNameAndUserIdAndIdNot(String name, Long userId, Long id);

    @Query("SELECT COALESCE(MAX(c.sortOrder), 0) FROM Category c WHERE c.userId = :userId")
    Integer findMaxSortOrderByUserId(@Param("userId") Long userId);

    // 根据名称和用户ID查找分类
    Category findByNameAndUserId(String name, Long userId);

    // 删除用户的所有分类
    @Modifying
    @Query("DELETE FROM Category c WHERE c.userId = :userId")
    void deleteAllByUserId(@Param("userId") Long userId);
}
