"""
人脸签到考勤系统 - 主应用入口
"""
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import config
import database
import face_service

# 创建 FastAPI 应用
app = FastAPI(
    title="人脸签到考勤系统",
    description="基于人脸识别的考勤管理系统 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=str(config.UPLOAD_DIR)), name="uploads")


# ==================== 响应模型 ====================

class ApiResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: Optional[dict] = None


def success_response(data=None, message="操作成功", code=200):
    return {"success": True, "code": code, "message": message, "data": data}


def error_response(message="操作失败", code=400, data=None):
    return {"success": False, "code": code, "message": message, "data": data}


# ==================== 请求模型 ====================

class EmployeeCreate(BaseModel):
    employeeId: str
    name: str
    department: Optional[str] = None
    position: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class FaceDetectRequest(BaseModel):
    image: str  # Base64 图片


class FaceRegisterRequest(BaseModel):
    employeeId: str
    imageUrls: List[str]


class AttendanceRequest(BaseModel):
    image: str  # Base64 图片


class SettingsUpdate(BaseModel):
    workStartTime: Optional[str] = None
    workEndTime: Optional[str] = None
    lateThreshold: Optional[int] = None
    earlyThreshold: Optional[int] = None
    recognitionThreshold: Optional[float] = None


# ==================== 员工管理接口 ====================

@app.get("/api/employees")
async def get_employees(
    keyword: Optional[str] = None,
    department: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """获取员工列表"""
    try:
        data = database.get_employees(keyword, department, page, size)
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)


@app.get("/api/employees/{employee_id}")
async def get_employee(employee_id: str):
    """获取单个员工"""
    employee = database.get_employee(employee_id)
    if not employee:
        return error_response("员工不存在", 404)
    return success_response(employee)


@app.post("/api/employees")
async def add_employee(data: EmployeeCreate):
    """添加员工"""
    try:
        # 检查工号是否已存在
        existing = database.get_employee(data.employeeId)
        if existing:
            return error_response("工号已存在", 400)
        
        employee = database.add_employee(
            data.employeeId, data.name, data.department, data.position
        )
        return success_response(employee, "添加成功", 201)
    except Exception as e:
        return error_response(str(e), 500)


@app.put("/api/employees/{employee_id}")
async def update_employee(employee_id: str, data: EmployeeUpdate):
    """更新员工信息"""
    existing = database.get_employee(employee_id)
    if not existing:
        return error_response("员工不存在", 404)
    
    try:
        employee = database.update_employee(
            employee_id, data.name, data.department, data.position
        )
        return success_response(employee, "更新成功")
    except Exception as e:
        return error_response(str(e), 500)


@app.delete("/api/employees/{employee_id}")
async def delete_employee(employee_id: str):
    """删除员工"""
    existing = database.get_employee(employee_id)
    if not existing:
        return error_response("员工不存在", 404)
    
    try:
        # 删除人脸图片
        if existing.get("faceImage"):
            face_path = config.BASE_DIR / existing["faceImage"].lstrip("/")
            if face_path.exists():
                face_path.unlink()
        
        database.delete_employee(employee_id)
        return success_response(None, "删除成功")
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 人脸管理接口 ====================

@app.post("/api/face/detect")
async def detect_face(data: FaceDetectRequest):
    """检测人脸"""
    try:
        result = face_service.detect_and_save_face(data.image)
        
        if result.get("faceDetected"):
            return success_response(result, "检测成功")
        else:
            return error_response("未检测到人脸，请调整拍摄角度", 422, result)
    except Exception as e:
        return error_response(str(e), 500)


@app.post("/api/face/upload")
async def upload_face(
    employeeId: str = Form(...),
    image: UploadFile = File(...)
):
    """上传人脸照片"""
    try:
        # 检查员工是否存在
        employee = database.get_employee(employeeId)
        if not employee:
            return error_response("员工不存在", 404)
        
        # 读取图片
        contents = await image.read()
        
        # 检查大小
        if len(contents) > config.MAX_IMAGE_SIZE:
            return error_response("图片大小超过限制", 400)
        
        # 保存临时文件
        import base64
        base64_image = f"data:image/jpeg;base64,{base64.b64encode(contents).decode()}"
        result = face_service.detect_and_save_face(base64_image)
        
        if result.get("faceDetected"):
            return success_response(result, "人脸检测成功")
        else:
            return error_response("未检测到人脸，请调整拍摄角度", 422)
    except Exception as e:
        return error_response(str(e), 500)


@app.post("/api/face/register")
async def register_face(data: FaceRegisterRequest):
    """注册人脸"""
    try:
        result = face_service.register_face(data.employeeId, data.imageUrls)
        
        if "error" in result:
            return error_response(result["message"], 400)
        
        return success_response(result, "人脸注册成功")
    except Exception as e:
        return error_response(str(e), 500)


@app.delete("/api/face/{employee_id}")
async def delete_face(employee_id: str):
    """删除人脸数据"""
    employee = database.get_employee(employee_id)
    if not employee:
        return error_response("员工不存在", 404)
    
    try:
        # 删除人脸图片
        if employee.get("faceImage"):
            face_path = config.BASE_DIR / employee["faceImage"].lstrip("/")
            if face_path.exists():
                face_path.unlink()
        
        database.delete_employee_face(employee_id)
        return success_response(None, "人脸数据已删除")
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 签到考勤接口 ====================

@app.post("/api/attendance/check-in")
async def check_in(data: AttendanceRequest):
    """人脸签到"""
    try:
        result = face_service.process_attendance(data.image, "check_in")
        
        if "error" in result:
            error_code = {
                "no_face": 422,
                "not_recognized": 404,
                "already_checked_in": 400,
                "no_registered": 400
            }.get(result["error"], 400)
            return error_response(result["message"], error_code, result)
        
        status_msg = "签到成功"
        if result.get("status") == "迟到":
            status_msg = "签到成功（迟到）"
        
        return success_response(result, status_msg)
    except Exception as e:
        return error_response(str(e), 500)


@app.post("/api/attendance/check-out")
async def check_out(data: AttendanceRequest):
    """人脸签退"""
    try:
        result = face_service.process_attendance(data.image, "check_out")
        
        if "error" in result:
            error_code = {
                "no_face": 422,
                "not_recognized": 404,
                "not_checked_in": 400
            }.get(result["error"], 400)
            return error_response(result["message"], error_code, result)
        
        status_msg = "签退成功"
        if result.get("status") == "早退":
            status_msg = "签退成功（早退）"
        
        return success_response(result, status_msg)
    except Exception as e:
        return error_response(str(e), 500)


@app.get("/api/attendance/today")
async def get_today_attendance(employeeId: Optional[str] = None):
    """获取今日签到状态"""
    try:
        data = database.get_today_attendance(employeeId)
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 考勤记录接口 ====================

@app.get("/api/attendance/records")
async def get_attendance_records(
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    employeeId: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    includeAbsent: bool = Query(False, description="是否包含缺勤人员"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """查询考勤记录"""
    try:
        # 如果查询单日且需要包含缺勤人员
        if includeAbsent and startDate and startDate == endDate:
            data = database.get_attendance_with_absent(startDate)
            # 状态筛选
            if status:
                data["list"] = [r for r in data["list"] if r.get("checkInStatus") == status or r.get("checkOutStatus") == status]
                data["total"] = len(data["list"])
            # 部门筛选
            if department:
                data["list"] = [r for r in data["list"] if r.get("department") == department]
                data["total"] = len(data["list"])
            return success_response(data)
        
        data = database.get_attendance_records(
            startDate, endDate, employeeId, department, status, page, size
        )
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)


@app.get("/api/attendance/records/{employee_id}")
async def get_employee_attendance(employee_id: str, month: Optional[str] = None):
    """获取员工考勤详情"""
    employee = database.get_employee(employee_id)
    if not employee:
        return error_response("员工不存在", 404)
    
    try:
        # 计算日期范围
        if month:
            year, m = map(int, month.split("-"))
        else:
            now = datetime.now()
            year, m = now.year, now.month
        
        from calendar import monthrange
        days_in_month = monthrange(year, m)[1]
        start_date = f"{year}-{m:02d}-01"
        end_date = f"{year}-{m:02d}-{days_in_month:02d}"
        
        data = database.get_attendance_records(
            start_date, end_date, employee_id, page=1, size=100
        )
        
        # 统计
        records = data["list"]
        normal_count = sum(1 for r in records if r["status"] == "正常")
        late_count = sum(1 for r in records if r["status"] == "迟到")
        early_count = sum(1 for r in records if r["status"] == "早退")
        
        return success_response({
            "employeeId": employee_id,
            "name": employee["name"],
            "department": employee.get("department"),
            "month": f"{year}-{m:02d}",
            "summary": {
                "workDays": days_in_month,  # 简化处理
                "actualDays": len(records),
                "lateDays": late_count,
                "earlyDays": early_count,
                "absentDays": days_in_month - len(records),
                "attendanceRate": f"{len(records) / days_in_month * 100:.1f}%"
            },
            "records": records
        })
    except Exception as e:
        return error_response(str(e), 500)


@app.get("/api/attendance/export")
async def export_attendance(startDate: str, endDate: str):
    """导出考勤记录"""
    try:
        from openpyxl import Workbook
        import tempfile
        
        # 获取数据
        data = database.get_attendance_records(startDate, endDate, page=1, size=10000)
        records = data["list"]
        
        # 创建 Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "考勤记录"
        
        # 表头
        headers = ["工号", "姓名", "部门", "日期", "签到时间", "签退时间", "工作时长", "状态"]
        ws.append(headers)
        
        # 数据
        for record in records:
            ws.append([
                record["employeeId"],
                record["name"],
                record["department"] or "",
                record["date"],
                record["checkInTime"] or "",
                record["checkOutTime"] or "",
                record["workHours"] or "",
                record["status"]
            ])
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        
        return FileResponse(
            temp_file.name,
            filename=f"考勤记录_{startDate}_{endDate}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 统计接口 ====================

@app.get("/api/statistics/today")
async def get_today_stats():
    """获取今日概览"""
    try:
        data = database.get_today_stats()
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)


@app.get("/api/statistics/attendance")
async def get_attendance_stats(
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    department: Optional[str] = None
):
    """获取考勤统计"""
    try:
        # 简化实现，返回基本统计
        data = database.get_attendance_records(startDate, endDate, department=department, size=10000)
        records = data["list"]
        
        total = len(records)
        # 计算正常：签到正常且（无签退或签退正常）
        normal = sum(1 for r in records if r.get("checkInStatus") == "正常" and (not r.get("checkOutStatus") or r.get("checkOutStatus") == "正常"))
        late = sum(1 for r in records if r.get("checkInStatus") == "迟到")
        early = sum(1 for r in records if r.get("checkOutStatus") == "早退")
        
        return success_response({
            "period": {
                "startDate": startDate,
                "endDate": endDate
            },
            "overview": {
                "totalRecords": total,
                "normalCount": normal,
                "lateCount": late,
                "earlyCount": early,
                "attendanceRate": f"{normal / total * 100:.1f}%" if total > 0 else "0%"
            }
        })
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 设置接口 ====================

@app.get("/api/settings/attendance")
async def get_settings():
    """获取考勤设置"""
    try:
        data = database.get_settings()
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)


@app.put("/api/settings/attendance")
async def update_settings(data: SettingsUpdate):
    """更新考勤设置"""
    try:
        settings = data.model_dump(exclude_none=True)
        database.update_settings(settings)
        return success_response(database.get_settings(), "设置已保存")
    except Exception as e:
        return error_response(str(e), 500)


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("🚀 人脸签到考勤系统启动中...")
    database.init_database()
    print(f"✅ 服务已启动: http://localhost:{config.PORT}")
    print(f"📖 API 文档: http://localhost:{config.PORT}/docs")


# ==================== 入口 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
