package com.bookmarkmanager.config;

import com.bookmarkmanager.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Spring Security 配置
 */
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 禁用 CSRF（使用 JWT，不需要 CSRF）
            .csrf(csrf -> csrf.disable())
            
            // 配置 CORS
            .cors(cors -> {})
            
            // 配置 Session 管理（无状态）
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            
            // 配置请求授权
            .authorizeHttpRequests(auth -> auth
                // 允许访问的公开接口
                .requestMatchers("/api/auth/register", "/api/auth/login").permitAll()
                // H2 控制台
                .requestMatchers("/h2-console/**").permitAll()
                // OPTIONS 请求（CORS 预检）
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                // 其他请求需要认证
                .anyRequest().authenticated()
            )
            
            // 允许 H2 控制台使用 iframe
            .headers(headers -> headers.frameOptions(frame -> frame.disable()))
            
            // 添加 JWT 过滤器
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
