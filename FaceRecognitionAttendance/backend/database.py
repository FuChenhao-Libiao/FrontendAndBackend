"""
人脸签到考勤系统 - 数据库模块
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import config


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(config.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 员工表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                face_encoding BLOB,
                face_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 考勤记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                date DATE NOT NULL,
                check_in_time DATETIME,
                check_out_time DATETIME,
                check_in_status TEXT DEFAULT '正常',
                check_out_status TEXT,
                check_in_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
                UNIQUE(employee_id, date)
            )
        """)
        
        # 系统设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL
            )
        """)
        
        # 初始化默认设置
        for key, value in config.DEFAULT_SETTINGS.items():
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, str(value)))
        
        conn.commit()
        print("✅ 数据库初始化完成")


# ==================== 员工操作 ====================

def get_employees(keyword: str = None, department: str = None, 
                  page: int = 1, size: int = 20) -> Dict[str, Any]:
    """获取员工列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM employees WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (employee_id LIKE ? OR name LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if department:
            query += " AND department = ?"
            params.append(department)
        
        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([size, (page - 1) * size])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        employees = []
        for row in rows:
            employees.append({
                "id": row["id"],
                "employeeId": row["employee_id"],
                "name": row["name"],
                "department": row["department"],
                "position": row["position"],
                "hasFace": row["face_encoding"] is not None,
                "faceImage": row["face_image"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"]
            })
        
        return {
            "total": total,
            "page": page,
            "size": size,
            "list": employees
        }


def get_employee(employee_id: str) -> Optional[Dict[str, Any]]:
    """获取单个员工"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "id": row["id"],
            "employeeId": row["employee_id"],
            "name": row["name"],
            "department": row["department"],
            "position": row["position"],
            "hasFace": row["face_encoding"] is not None,
            "faceImage": row["face_image"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"]
        }


def add_employee(employee_id: str, name: str, 
                 department: str = None, position: str = None) -> Dict[str, Any]:
    """添加员工"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (employee_id, name, department, position)
            VALUES (?, ?, ?, ?)
        """, (employee_id, name, department, position))
        conn.commit()  # 确保提交
    
    # 在 with 块外部获取员工信息
    return get_employee(employee_id)


def update_employee(employee_id: str, name: str = None,
                    department: str = None, position: str = None) -> Optional[Dict[str, Any]]:
    """更新员工信息"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if department is not None:
            updates.append("department = ?")
            params.append(department)
        if position is not None:
            updates.append("position = ?")
            params.append(position)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE employees SET {', '.join(updates)} WHERE employee_id = ?"
            params.append(employee_id)
            cursor.execute(query, params)
        
        return get_employee(employee_id)


def delete_employee(employee_id: str) -> bool:
    """删除员工"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 删除考勤记录
        cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,))
        
        # 删除员工
        cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
        
        return cursor.rowcount > 0


def update_employee_face(employee_id: str, face_image: str = None, face_encoding: bytes = None) -> bool:
    """更新员工人脸数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE employees 
            SET face_encoding = ?, face_image = ?, updated_at = CURRENT_TIMESTAMP
            WHERE employee_id = ?
        """, (face_encoding, face_image, employee_id))
        conn.commit()
        
        return cursor.rowcount > 0


def delete_employee_face(employee_id: str) -> bool:
    """删除员工人脸数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE employees 
            SET face_encoding = NULL, face_image = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE employee_id = ?
        """, (employee_id,))
        
        return cursor.rowcount > 0


def get_all_face_encodings() -> List[Dict[str, Any]]:
    """获取所有已注册人脸编码"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT employee_id, name, department, face_encoding, face_image
            FROM employees 
            WHERE face_encoding IS NOT NULL
        """)
        
        result = []
        for row in cursor.fetchall():
            result.append({
                "employeeId": row["employee_id"],
                "name": row["name"],
                "department": row["department"],
                "faceEncoding": row["face_encoding"],
                "faceImage": row["face_image"]
            })
        
        return result


def get_registered_faces() -> List[Dict[str, Any]]:
    """获取所有已注册人脸（get_all_face_encodings的别名）"""
    return get_all_face_encodings()


def record_attendance(employee_id: str, is_check_in: bool = True, 
                      similarity: float = 0.0) -> Optional[Dict[str, Any]]:
    """
    记录考勤（签到或签退）
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    # 获取考勤设置
    settings = get_settings()
    work_start = settings.get("workStartTime", "09:00")
    work_end = settings.get("workEndTime", "18:00")
    late_threshold = settings.get("lateThreshold", 10)
    early_threshold = settings.get("earlyThreshold", 10)
    
    if is_check_in:
        # 签到 - 判断是否迟到
        work_start_time = datetime.strptime(f"{current_date} {work_start}:00", "%Y-%m-%d %H:%M:%S")
        late_deadline = work_start_time + timedelta(minutes=late_threshold)
        
        if now > late_deadline:
            status = "迟到"
        else:
            status = "正常"
        
        return check_in(employee_id, current_time, status)
    else:
        # 签退 - 判断是否早退
        work_end_time = datetime.strptime(f"{current_date} {work_end}:00", "%Y-%m-%d %H:%M:%S")
        early_deadline = work_end_time - timedelta(minutes=early_threshold)
        
        if now < early_deadline:
            status = "早退"
        else:
            status = "正常"
        
        return check_out(employee_id, current_time, status)


# ==================== 考勤操作 ====================

def get_today_attendance(employee_id: str = None) -> Dict[str, Any]:
    """获取今日考勤"""
    from datetime import date
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 总员工数
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]
        
        # 今日签到情况
        query = """
            SELECT a.*, e.name, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.date = ?
        """
        params = [today]
        
        if employee_id:
            query += " AND a.employee_id = ?"
            params.append(employee_id)
        
        query += " ORDER BY a.check_in_time DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        records = []
        checked_in = 0
        checked_out = 0
        
        for row in rows:
            checked_in += 1
            if row["check_out_time"]:
                checked_out += 1
            
            # 处理时间格式（可能是 HH:MM:SS 或 YYYY-MM-DD HH:MM:SS）
            check_in_time = row["check_in_time"]
            check_out_time = row["check_out_time"]
            
            if check_in_time and " " in check_in_time:
                check_in_time = check_in_time.split(" ")[1]
            if check_out_time and " " in check_out_time:
                check_out_time = check_out_time.split(" ")[1]
            
            records.append({
                "employeeId": row["employee_id"],
                "name": row["name"],
                "department": row["department"],
                "checkInTime": check_in_time,
                "checkOutTime": check_out_time,
                "checkInStatus": row["check_in_status"] if "check_in_status" in row.keys() else row.get("status"),
                "checkOutStatus": row["check_out_status"] if "check_out_status" in row.keys() else None
            })
        
        return {
            "date": today,
            "totalEmployees": total_employees,
            "checkedIn": checked_in,
            "checkedOut": checked_out,
            "records": records
        }


def check_in(employee_id: str, check_time: str, status: str, image_path: str = None) -> Dict[str, Any]:
    """签到"""
    from datetime import date
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查是否已签到
        cursor.execute("""
            SELECT * FROM attendance WHERE employee_id = ? AND date = ?
        """, (employee_id, today))
        
        if cursor.fetchone():
            return {"success": False, "message": "今日已签到", "time": check_time}
        
        # 插入签到记录
        cursor.execute("""
            INSERT INTO attendance (employee_id, date, check_in_time, check_in_status, check_in_image)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, today, check_time, status, image_path))
        conn.commit()
        
        return {"success": True, "time": check_time, "status": status}


def check_out(employee_id: str, check_time: str, status: str) -> Dict[str, Any]:
    """签退"""
    from datetime import date
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 更新签退时间和签退状态
        cursor.execute("""
            UPDATE attendance 
            SET check_out_time = ?, check_out_status = ?
            WHERE employee_id = ? AND date = ?
        """, (check_time, status, employee_id, today))
        conn.commit()
        
        return {"success": cursor.rowcount > 0, "time": check_time, "status": status}


def get_attendance_records(start_date: str = None, end_date: str = None,
                           employee_id: str = None, department: str = None,
                           status: str = None, page: int = 1, size: int = 20) -> Dict[str, Any]:
    """获取考勤记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT a.*, e.name, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND a.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= ?"
            params.append(end_date)
        
        if employee_id:
            query += " AND a.employee_id = ?"
            params.append(employee_id)
        
        if department:
            query += " AND e.department = ?"
            params.append(department)
        
        if status:
            # 状态筛选：迟到查签到状态，早退查签退状态
            if status == "迟到":
                query += " AND a.check_in_status = ?"
                params.append(status)
            elif status == "早退":
                query += " AND a.check_out_status = ?"
                params.append(status)
            elif status == "正常":
                query += " AND a.check_in_status = ? AND (a.check_out_status IS NULL OR a.check_out_status = ?)"
                params.extend(["正常", "正常"])
        
        # 获取总数
        count_query = query.replace("SELECT a.*, e.name, e.department", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页
        query += " ORDER BY a.date DESC, a.check_in_time DESC LIMIT ? OFFSET ?"
        params.extend([size, (page - 1) * size])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 状态映射（兼容旧数据）
        status_map = {
            "normal": "正常",
            "late": "迟到", 
            "early": "早退",
            "absent": "缺勤",
            "正常": "正常",
            "迟到": "迟到",
            "早退": "早退",
            "缺勤": "缺勤"
        }
        
        records = []
        for row in rows:
            work_hours = None
            check_in_time = row["check_in_time"]
            check_out_time = row["check_out_time"]
            
            # 处理时间格式（可能是 HH:MM:SS 或 YYYY-MM-DD HH:MM:SS）
            if check_in_time and " " in check_in_time:
                check_in_time = check_in_time.split(" ")[1]
            if check_out_time and " " in check_out_time:
                check_out_time = check_out_time.split(" ")[1]
            
            # 计算工作时长
            if check_in_time and check_out_time:
                from datetime import datetime
                try:
                    t1 = datetime.strptime(check_in_time, "%H:%M:%S")
                    t2 = datetime.strptime(check_out_time, "%H:%M:%S")
                    diff = t2 - t1
                    total_seconds = diff.seconds
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    work_hours = f"{hours}小时{minutes}分钟"
                except Exception as e:
                    work_hours = "-"
            
            # 转换状态为中文 - 分别处理签到状态和签退状态
            raw_check_in_status = row["check_in_status"] if "check_in_status" in row.keys() else (row["status"] if "status" in row.keys() else "正常")
            raw_check_out_status = row["check_out_status"] if "check_out_status" in row.keys() else None
            
            check_in_status = status_map.get(raw_check_in_status, raw_check_in_status) if raw_check_in_status else None
            check_out_status = status_map.get(raw_check_out_status, raw_check_out_status) if raw_check_out_status else None
            
            records.append({
                "id": row["id"],
                "employeeId": row["employee_id"],
                "name": row["name"],
                "department": row["department"],
                "date": row["date"],
                "checkInTime": check_in_time,
                "checkOutTime": check_out_time,
                "checkInStatus": check_in_status,
                "checkOutStatus": check_out_status,
                "workHours": work_hours
            })
        
        return {
            "total": total,
            "page": page,
            "size": size,
            "list": records
        }


def get_attendance_with_absent(target_date: str = None) -> Dict[str, Any]:
    """获取考勤记录（包含缺勤人员）"""
    from datetime import date, datetime
    
    if not target_date:
        target_date = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取所有员工
        cursor.execute("SELECT employee_id, name, department FROM employees")
        all_employees = {row["employee_id"]: {"name": row["name"], "department": row["department"]} 
                        for row in cursor.fetchall()}
        
        # 获取当天已签到的记录
        cursor.execute("""
            SELECT a.*, e.name, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.date = ?
            ORDER BY a.check_in_time DESC
        """, (target_date,))
        
        attendance_records = cursor.fetchall()
        checked_in_ids = set()
        
        records = []
        for row in attendance_records:
            checked_in_ids.add(row["employee_id"])
            
            check_in_time = row["check_in_time"]
            check_out_time = row["check_out_time"]
            
            if check_in_time and " " in check_in_time:
                check_in_time = check_in_time.split(" ")[1]
            if check_out_time and " " in check_out_time:
                check_out_time = check_out_time.split(" ")[1]
            
            # 计算工作时长
            work_hours = None
            if check_in_time and check_out_time:
                try:
                    t1 = datetime.strptime(check_in_time, "%H:%M:%S")
                    t2 = datetime.strptime(check_out_time, "%H:%M:%S")
                    diff = t2 - t1
                    total_seconds = diff.seconds
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    work_hours = f"{hours}小时{minutes}分钟"
                except:
                    work_hours = "-"
            
            records.append({
                "employeeId": row["employee_id"],
                "name": row["name"],
                "department": row["department"],
                "date": row["date"],
                "checkInTime": check_in_time,
                "checkOutTime": check_out_time,
                "checkInStatus": row["check_in_status"] if "check_in_status" in row.keys() else "正常",
                "checkOutStatus": row["check_out_status"] if "check_out_status" in row.keys() else None,
                "workHours": work_hours
            })
        
        # 添加缺勤人员
        for emp_id, emp_info in all_employees.items():
            if emp_id not in checked_in_ids:
                records.append({
                    "employeeId": emp_id,
                    "name": emp_info["name"],
                    "department": emp_info["department"],
                    "date": target_date,
                    "checkInTime": None,
                    "checkOutTime": None,
                    "checkInStatus": "缺勤",
                    "checkOutStatus": None,
                    "workHours": None
                })
        
        return {
            "date": target_date,
            "total": len(records),
            "list": records
        }


# ==================== 设置操作 ====================

def get_settings() -> Dict[str, Any]:
    """获取系统设置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        
        settings = {}
        for row in cursor.fetchall():
            key = row["key"]
            value = row["value"]
            
            # 转换类型
            if key in ["late_threshold", "early_threshold"]:
                value = int(value)
            elif key == "recognition_threshold":
                value = float(value)
            
            # 转换为驼峰命名
            camel_key = "".join(word.capitalize() if i > 0 else word 
                               for i, word in enumerate(key.split("_")))
            settings[camel_key] = value
        
        return settings


def update_settings(settings: Dict[str, Any]) -> bool:
    """更新系统设置"""
    # 将驼峰转下划线
    key_map = {
        "workStartTime": "work_start_time",
        "workEndTime": "work_end_time",
        "lateThreshold": "late_threshold",
        "earlyThreshold": "early_threshold",
        "recognitionThreshold": "recognition_threshold"
    }
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for camel_key, value in settings.items():
            snake_key = key_map.get(camel_key, camel_key)
            cursor.execute("""
                UPDATE settings SET value = ? WHERE key = ?
            """, (str(value), snake_key))
        
        return True


# ==================== 统计操作 ====================

def get_today_stats() -> Dict[str, Any]:
    """获取今日统计"""
    from datetime import date, datetime
    today = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 总员工数
        cursor.execute("SELECT COUNT(*) FROM employees")
        total = cursor.fetchone()[0]
        
        # 今日签到数
        cursor.execute("""
            SELECT COUNT(*) FROM attendance WHERE date = ?
        """, (today,))
        checked_in = cursor.fetchone()[0]
        
        # 今日签退数
        cursor.execute("""
            SELECT COUNT(*) FROM attendance WHERE date = ? AND check_out_time IS NOT NULL
        """, (today,))
        checked_out = cursor.fetchone()[0]
        
        # 迟到数
        cursor.execute("""
            SELECT COUNT(*) FROM attendance WHERE date = ? AND check_in_status = '迟到'
        """, (today,))
        late_count = cursor.fetchone()[0]
        
        # 早退数
        cursor.execute("""
            SELECT COUNT(*) FROM attendance WHERE date = ? AND check_out_status = '早退'
        """, (today,))
        early_count = cursor.fetchone()[0]
        
        # 最近签到记录
        cursor.execute("""
            SELECT a.*, e.name FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.date = ?
            ORDER BY a.check_in_time DESC
            LIMIT 10
        """, (today,))
        
        recent = []
        for row in cursor.fetchall():
            time_str = row["check_out_time"] or row["check_in_time"]
            if time_str and " " in time_str:
                time_str = time_str.split(" ")[1]
            recent.append({
                "employeeId": row["employee_id"],
                "name": row["name"],
                "action": "签退" if row["check_out_time"] else "签到",
                "time": time_str,
                "checkInStatus": row["check_in_status"] if "check_in_status" in row.keys() else None,
                "checkOutStatus": row["check_out_status"] if "check_out_status" in row.keys() else None
            })
        
        return {
            "date": today,
            "currentTime": datetime.now().strftime("%H:%M:%S"),
            "totalEmployees": total,
            "checkedIn": checked_in,
            "notCheckedIn": total - checked_in,
            "checkedOut": checked_out,
            "lateCount": late_count,
            "earlyCount": early_count,
            "attendanceRate": f"{(checked_in / total * 100):.1f}%" if total > 0 else "0%",
            "recentRecords": recent
        }


if __name__ == "__main__":
    init_database()
