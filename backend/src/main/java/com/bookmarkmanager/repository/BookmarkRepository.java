package com.bookmarkmanager.repository;

import com.bookmarkmanager.entity.Bookmark;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 书签数据访问层
 */
@Repository
public interface BookmarkRepository extends JpaRepository<Bookmark, Long> {

    // 分页查询用户的所有书签
    Page<Bookmark> findByUserIdOrderBySortOrderAsc(Long userId, Pageable pageable);

    // 按分类查询
    Page<Bookmark> findByUserIdAndCategoryIdOrderBySortOrderAsc(Long userId, Long categoryId, Pageable pageable);

    // 搜索书签
    @Query("SELECT b FROM Bookmark b WHERE b.userId = :userId AND " +
           "(LOWER(b.title) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(b.description) LIKE LOWER(CONCAT('%', :keyword, '%')))")
    Page<Bookmark> searchByKeyword(@Param("userId") Long userId, @Param("keyword") String keyword, Pageable pageable);

    // 按分类和关键词搜索
    @Query("SELECT b FROM Bookmark b WHERE b.userId = :userId AND b.categoryId = :categoryId AND " +
           "(LOWER(b.title) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(b.description) LIKE LOWER(CONCAT('%', :keyword, '%')))")
    Page<Bookmark> searchByCategoryAndKeyword(@Param("userId") Long userId, 
                                               @Param("categoryId") Long categoryId,
                                               @Param("keyword") String keyword, 
                                               Pageable pageable);

    // 根据ID和用户ID查询
    Optional<Bookmark> findByIdAndUserId(Long id, Long userId);

    // 查询分类下的书签数量
    long countByCategoryId(Long categoryId);

    // 查询用户的书签数量
    long countByUserId(Long userId);

    // 获取分类下的所有书签
    List<Bookmark> findByUserIdAndCategoryIdOrderBySortOrderAsc(Long userId, Long categoryId);

    // 获取用户的所有书签（用于导出）
    List<Bookmark> findByUserIdOrderBySortOrderAsc(Long userId);

    // 获取最大排序号
    @Query("SELECT COALESCE(MAX(b.sortOrder), 0) FROM Bookmark b WHERE b.userId = :userId")
    Integer findMaxSortOrderByUserId(@Param("userId") Long userId);

    // 批量删除
    @Modifying
    @Query("DELETE FROM Bookmark b WHERE b.id IN :ids AND b.userId = :userId")
    void deleteByIdsAndUserId(@Param("ids") List<Long> ids, @Param("userId") Long userId);

    // 将分类下的书签设为未分类
    @Modifying
    @Query("UPDATE Bookmark b SET b.categoryId = null WHERE b.categoryId = :categoryId")
    void clearCategoryId(@Param("categoryId") Long categoryId);

    // 检查URL是否已存在
    boolean existsByUrlAndUserId(String url, Long userId);

    // 删除用户的所有书签
    @Modifying
    @Query("DELETE FROM Bookmark b WHERE b.userId = :userId")
    void deleteAllByUserId(@Param("userId") Long userId);
}
