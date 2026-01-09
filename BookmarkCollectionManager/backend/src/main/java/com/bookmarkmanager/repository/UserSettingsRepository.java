package com.bookmarkmanager.repository;

import com.bookmarkmanager.entity.UserSettings;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * 用户设置数据访问层
 */
@Repository
public interface UserSettingsRepository extends JpaRepository<UserSettings, Long> {

    Optional<UserSettings> findByUserId(Long userId);

    // 删除用户的设置
    void deleteByUserId(Long userId);
}
