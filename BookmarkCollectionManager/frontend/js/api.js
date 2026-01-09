/**
 * API 服务层
 * 统一管理所有与后端的 HTTP 请求
 */

const API = {
    // 后端基础URL - 开发环境
    BASE_URL: 'http://localhost:8080/api',

    // 获取存储的 Token
    getToken() {
        return localStorage.getItem('token');
    },

    // 设置 Token
    setToken(token) {
        localStorage.setItem('token', token);
    },

    // 清除 Token
    clearToken() {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
    },

    // 统一请求方法
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const token = this.getToken();

        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // 添加认证头
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        // 处理请求体
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            // 处理 401 未授权 - 但排除登录接口（登录失败也是401）
            if (response.status === 401 && !endpoint.includes('/auth/login')) {
                this.clearToken();
                window.location.href = 'login.html';
                return { success: false, message: '登录已过期，请重新登录' };
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            return {
                success: false,
                message: '网络请求失败，请检查网络连接'
            };
        }
    },

    // ===== 认证相关 API =====
    auth: {
        // 登录
        async login(username, password) {
            return API.request('/auth/login', {
                method: 'POST',
                body: { username, password }
            });
        },

        // 注册
        async register(username, password, email = null) {
            const body = { username, password };
            if (email) body.email = email;
            return API.request('/auth/register', {
                method: 'POST',
                body
            });
        },

        // 获取当前用户信息
        async getCurrentUser() {
            return API.request('/auth/me');
        },

        // 更新用户资料
        async updateProfile(data) {
            return API.request('/auth/profile', {
                method: 'PUT',
                body: data
            });
        },

        // 修改密码
        async changePassword(currentPassword, newPassword) {
            return API.request('/auth/password', {
                method: 'PUT',
                body: { currentPassword, newPassword }
            });
        },

        // 获取用户设置
        async getSettings() {
            return API.request('/auth/settings');
        },

        // 更新用户设置
        async updateSettings(settings) {
            return API.request('/auth/settings', {
                method: 'PUT',
                body: settings
            });
        },

        // 退出登录
        async logout() {
            const result = await API.request('/auth/logout', {
                method: 'POST'
            });
            API.clearToken();
            return result;
        },

        // 注销账户
        async deleteAccount(password) {
            return API.request('/auth/account', {
                method: 'DELETE',
                body: { password }
            });
        }
    },

    // ===== 书签相关 API =====
    bookmarks: {
        // 获取书签列表
        async getList(params = {}) {
            const queryParams = new URLSearchParams();
            if (params.categoryId) queryParams.append('categoryId', params.categoryId);
            if (params.keyword) queryParams.append('keyword', params.keyword);
            if (params.page) queryParams.append('page', params.page);
            if (params.size) queryParams.append('size', params.size);

            const queryString = queryParams.toString();
            const endpoint = queryString ? `/bookmarks?${queryString}` : '/bookmarks';
            return API.request(endpoint);
        },

        // 获取单个书签
        async getById(id) {
            return API.request(`/bookmarks/${id}`);
        },

        // 创建书签
        async create(data) {
            return API.request('/bookmarks', {
                method: 'POST',
                body: data
            });
        },

        // 更新书签
        async update(id, data) {
            return API.request(`/bookmarks/${id}`, {
                method: 'PUT',
                body: data
            });
        },

        // 删除书签
        async delete(id) {
            return API.request(`/bookmarks/${id}`, {
                method: 'DELETE'
            });
        },

        // 批量删除书签
        async batchDelete(ids) {
            return API.request('/bookmarks/batch', {
                method: 'DELETE',
                body: { ids }
            });
        },

        // 移动书签到分类
        async move(id, targetCategoryId) {
            return API.request(`/bookmarks/${id}/move`, {
                method: 'PUT',
                body: { targetCategoryId }
            });
        },

        // 批量移动书签
        async batchMove(ids, categoryId) {
            return API.request('/bookmarks/batch/move', {
                method: 'PUT',
                body: { ids, categoryId }
            });
        },

        // 书签排序
        async reorder(bookmarkIds, categoryId = null) {
            const body = { bookmarkIds };
            if (categoryId !== null) body.categoryId = categoryId;
            return API.request('/bookmarks/reorder', {
                method: 'PUT',
                body
            });
        }
    },

    // ===== 分类相关 API =====
    categories: {
        // 获取分类列表
        async getList() {
            return API.request('/categories');
        },

        // 获取单个分类
        async getById(id) {
            return API.request(`/categories/${id}`);
        },

        // 创建分类
        async create(data) {
            return API.request('/categories', {
                method: 'POST',
                body: data
            });
        },

        // 更新分类
        async update(id, data) {
            return API.request(`/categories/${id}`, {
                method: 'PUT',
                body: data
            });
        },

        // 删除分类
        async delete(id) {
            return API.request(`/categories/${id}`, {
                method: 'DELETE'
            });
        },

        // 分类排序
        async reorder(categoryIds) {
            return API.request('/categories/reorder', {
                method: 'PUT',
                body: { categoryIds }
            });
        }
    },

    // ===== 数据管理 API =====
    data: {
        // 导出数据
        async exportData() {
            return API.request('/auth/export');
        },

        // 导入数据
        async importData(data) {
            return API.request('/auth/import', {
                method: 'POST',
                body: data
            });
        },

        // 清空所有数据
        async clearAll() {
            return API.request('/auth/data/clear', {
                method: 'DELETE'
            });
        }
    },

    // ===== 统计相关 API =====
    statistics: {
        // 获取统计数据
        async get() {
            return API.request('/statistics');
        }
    }
};

// 兼容旧版 MockAPI 的接口，方便逐步迁移
const MockAPI = {
    delay: (ms = 0) => Promise.resolve(),
    response: (success, data = null, message = '') => ({ success, data, message }),

    bookmarks: {
        getList: async (params) => API.bookmarks.getList(params),
        create: async (data) => API.bookmarks.create(data),
        update: async (id, data) => API.bookmarks.update(id, data),
        delete: async (id) => API.bookmarks.delete(id)
    },

    categories: {
        getList: async () => API.categories.getList(),
        create: async (data) => API.categories.create(data),
        update: async (id, data) => API.categories.update(id, data),
        delete: async (id) => API.categories.delete(id)
    },

    statistics: {
        get: async () => API.statistics.get()
    }
};
