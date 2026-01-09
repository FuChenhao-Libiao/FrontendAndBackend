package com.bookmarkmanager.controller;

import com.bookmarkmanager.dto.ApiResponse;
import com.bookmarkmanager.dto.statistics.StatisticsResponse;
import com.bookmarkmanager.service.StatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 统计控制器
 */
@RestController
@RequestMapping("/api/statistics")
@RequiredArgsConstructor
public class StatisticsController {

    private final StatisticsService statisticsService;

    /**
     * 获取统计概览
     */
    @GetMapping
    public ResponseEntity<ApiResponse<StatisticsResponse>> getStatistics(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        StatisticsResponse statistics = statisticsService.getStatistics(userId);
        return ResponseEntity.ok(ApiResponse.success("查询成功", statistics));
    }
}
