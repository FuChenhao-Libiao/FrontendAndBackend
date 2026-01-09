/**
 * 人脸签到考勤系统 - API 接口封装
 * @version 1.0
 */

const API_BASE_URL = 'http://localhost:8081/api';

// 通用请求方法
async function request(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE_URL}${url}`, mergedOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// API 接口对象
const api = {
    // ==================== 员工管理 ====================
    
    /**
     * 获取员工列表
     * @param {Object} params - 查询参数
     */
    getEmployees: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return request(`/employees${queryString ? '?' + queryString : ''}`);
    },

    /**
     * 获取单个员工
     * @param {string} employeeId - 员工工号
     */
    getEmployee: async (employeeId) => {
        return request(`/employees/${employeeId}`);
    },

    /**
     * 添加员工
     * @param {Object} data - 员工数据
     */
    addEmployee: async (data) => {
        return request('/employees', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * 更新员工信息
     * @param {string} employeeId - 员工工号
     * @param {Object} data - 更新数据
     */
    updateEmployee: async (employeeId, data) => {
        return request(`/employees/${employeeId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * 删除员工
     * @param {string} employeeId - 员工工号
     */
    deleteEmployee: async (employeeId) => {
        return request(`/employees/${employeeId}`, {
            method: 'DELETE',
        });
    },

    // ==================== 人脸管理 ====================

    /**
     * 检测人脸（Base64图片）
     * @param {string} imageBase64 - Base64编码的图片
     */
    detectFace: async (imageBase64) => {
        return request('/face/detect', {
            method: 'POST',
            body: JSON.stringify({ image: imageBase64 }),
        });
    },

    /**
     * 上传人脸照片
     * @param {string} employeeId - 员工工号
     * @param {File} imageFile - 图片文件
     */
    uploadFace: async (employeeId, imageFile) => {
        const formData = new FormData();
        formData.append('employeeId', employeeId);
        formData.append('image', imageFile);

        return fetch(`${API_BASE_URL}/face/upload`, {
            method: 'POST',
            body: formData,
        }).then(res => res.json());
    },

    /**
     * 注册人脸
     * @param {Object} data - {employeeId, imageUrls}
     */
    registerFace: async (data) => {
        return request('/face/register', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * 删除人脸数据
     * @param {string} employeeId - 员工工号
     */
    deleteFace: async (employeeId) => {
        return request(`/face/${employeeId}`, {
            method: 'DELETE',
        });
    },

    // ==================== 签到考勤 ====================

    /**
     * 人脸签到
     * @param {string} imageBase64 - Base64编码的图片
     */
    checkIn: async (imageBase64) => {
        return request('/attendance/check-in', {
            method: 'POST',
            body: JSON.stringify({ image: imageBase64 }),
        });
    },

    /**
     * 人脸签退
     * @param {string} imageBase64 - Base64编码的图片
     */
    checkOut: async (imageBase64) => {
        return request('/attendance/check-out', {
            method: 'POST',
            body: JSON.stringify({ image: imageBase64 }),
        });
    },

    /**
     * 获取今日签到记录
     */
    getTodayRecords: async () => {
        return request('/attendance/today');
    },

    /**
     * 获取今日统计
     */
    getTodayStats: async () => {
        return request('/statistics/today');
    },

    // ==================== 考勤记录 ====================

    /**
     * 查询考勤记录
     * @param {Object} params - 查询参数
     */
    getAttendanceRecords: async (params = {}) => {
        const queryString = new URLSearchParams(
            Object.fromEntries(
                Object.entries(params).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
            )
        ).toString();
        return request(`/attendance/records${queryString ? '?' + queryString : ''}`);
    },

    /**
     * 获取员工考勤详情
     * @param {string} employeeId - 员工工号
     * @param {string} month - 月份（YYYY-MM）
     */
    getEmployeeAttendance: async (employeeId, month) => {
        return request(`/attendance/records/${employeeId}${month ? '?month=' + month : ''}`);
    },

    /**
     * 导出考勤记录
     * @param {string} startDate - 开始日期
     * @param {string} endDate - 结束日期
     */
    exportRecords: async (startDate, endDate) => {
        const url = `${API_BASE_URL}/attendance/export?startDate=${startDate}&endDate=${endDate}`;
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = url;
        link.download = `考勤记录_${startDate}_${endDate}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    // ==================== 统计报表 ====================

    /**
     * 获取考勤统计
     * @param {Object} params - 查询参数
     */
    getAttendanceStats: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return request(`/statistics/attendance${queryString ? '?' + queryString : ''}`);
    },

    // ==================== 系统设置 ====================

    /**
     * 获取考勤设置
     */
    getSettings: async () => {
        return request('/settings/attendance');
    },

    /**
     * 保存考勤设置
     * @param {Object} data - 设置数据
     */
    saveSettings: async (data) => {
        return request('/settings/attendance', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
};

// 导出 API 对象（兼容不同模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
}
