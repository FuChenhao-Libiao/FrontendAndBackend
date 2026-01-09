"""
人脸签到考勤系统 - 人脸识别模块
使用 OpenCV 进行人脸检测（Haar Cascade）
使用简化的图像特征进行人脸比对
"""
import base64
import io
import pickle
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

import cv2
import numpy as np
from PIL import Image

import config

# 加载 OpenCV 人脸检测器
_face_cascade = None


def _get_face_cascade():
    """获取人脸检测器"""
    global _face_cascade
    if _face_cascade is None:
        # 使用 OpenCV 自带的 Haar Cascade 分类器
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    解码 Base64 图片为 numpy 数组（RGB格式）
    """
    # 移除 data URL 前缀
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    # 解码 Base64
    image_data = base64.b64decode(base64_string)
    
    # 转为 PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # 转为 RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # 转为 numpy 数组 (RGB)
    image_array = np.array(image)
    
    return image_array


def save_base64_image(base64_string: str, save_path: Path) -> str:
    """
    保存 Base64 图片到文件
    返回保存的文件路径
    """
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    image.save(save_path, "JPEG", quality=90)
    return str(save_path)


def detect_faces(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    使用 OpenCV Haar Cascade 检测图片中的人脸位置
    返回人脸位置列表
    """
    cascade = _get_face_cascade()
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # 检测人脸
    faces_rect = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )
    
    faces = []
    for (x, y, w, h) in faces_rect:
        faces.append({
            "top": int(y),
            "right": int(x + w),
            "bottom": int(y + h),
            "left": int(x),
            "confidence": 0.9  # Haar Cascade 不提供置信度，使用固定值
        })
    
    return faces


def get_face_encoding(image: np.ndarray, face_location: Dict = None) -> Optional[np.ndarray]:
    """
    提取人脸特征编码
    使用 LBPH (Local Binary Patterns Histograms) 特征
    """
    # 如果提供了人脸位置，先裁剪
    if face_location:
        top = face_location.get("top", 0)
        bottom = face_location.get("bottom", image.shape[0])
        left = face_location.get("left", 0)
        right = face_location.get("right", image.shape[1])
        
        # 扩展边界
        h, w = image.shape[:2]
        pad = 10
        top = max(0, top - pad)
        bottom = min(h, bottom + pad)
        left = max(0, left - pad)
        right = min(w, right + pad)
        
        face_image = image[top:bottom, left:right]
    else:
        # 检测人脸
        faces = detect_faces(image)
        if not faces:
            return None
        face = faces[0]
        face_image = image[face["top"]:face["bottom"], face["left"]:face["right"]]
    
    # 确保图像足够大
    if face_image.shape[0] < 10 or face_image.shape[1] < 10:
        return None
    
    # 转为灰度图
    if len(face_image.shape) == 3:
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
    else:
        gray = face_image
    
    # 调整到统一大小
    resized = cv2.resize(gray, (128, 128))
    
    # 计算 LBP 直方图作为特征
    # 简化版：将图像分成 8x8 网格，每个网格计算直方图
    encoding = []
    grid_size = 16  # 128 / 8 = 16
    
    for i in range(8):
        for j in range(8):
            cell = resized[i*grid_size:(i+1)*grid_size, j*grid_size:(j+1)*grid_size]
            # 计算简单的统计特征
            hist, _ = np.histogram(cell, bins=16, range=(0, 256))
            hist = hist.astype(np.float32)
            hist /= (hist.sum() + 1e-7)  # 归一化
            encoding.extend(hist)
    
    return np.array(encoding, dtype=np.float32)


def compare_faces(known_encoding: np.ndarray, unknown_encoding: np.ndarray, 
                  threshold: float = None) -> Tuple[bool, float]:
    """
    比较两个人脸编码
    使用余弦相似度
    返回 (是否匹配, 相似度)
    """
    if threshold is None:
        threshold = config.DEFAULT_SETTINGS["recognition_threshold"]
    
    # 确保两个编码长度相同
    if len(known_encoding) != len(unknown_encoding):
        return False, 0.0
    
    # 计算余弦相似度
    dot_product = np.dot(known_encoding, unknown_encoding)
    norm_a = np.linalg.norm(known_encoding)
    norm_b = np.linalg.norm(unknown_encoding)
    
    if norm_a == 0 or norm_b == 0:
        return False, 0.0
    
    similarity = dot_product / (norm_a * norm_b)
    similarity = float(max(0, min(1, similarity)))  # 限制在 0-1 范围
    
    # 判断是否匹配
    is_match = similarity >= threshold
    
    return is_match, similarity


def recognize_face(image: np.ndarray, known_faces: List[Dict[str, Any]], 
                   threshold: float = None) -> Optional[Dict[str, Any]]:
    """
    在已知人脸库中识别人脸
    返回匹配的员工信息，如果没有匹配返回 None
    """
    if threshold is None:
        import database
        settings = database.get_settings()
        threshold = settings.get("recognitionThreshold", config.DEFAULT_SETTINGS["recognition_threshold"])
    
    # 先检测人脸
    faces = detect_faces(image)
    
    if not faces:
        return {"error": "no_face", "message": "未检测到人脸"}
    
    # 获取待识别图片的人脸编码
    unknown_encoding = get_face_encoding(image, faces[0])
    
    if unknown_encoding is None:
        return {"error": "encoding_failed", "message": "无法提取人脸特征"}
    
    best_match = None
    best_similarity = 0
    
    for known in known_faces:
        # 反序列化已存储的编码
        try:
            known_encoding = pickle.loads(known["faceEncoding"])
        except:
            continue
        
        is_match, similarity = compare_faces(known_encoding, unknown_encoding, threshold)
        
        if is_match and similarity > best_similarity:
            best_similarity = similarity
            best_match = {
                "employeeId": known["employeeId"],
                "name": known["name"],
                "department": known.get("department", ""),
                "faceImage": known.get("faceImage", ""),
                "similarity": similarity
            }
    
    return best_match


def detect_and_save_face(base64_image: str) -> Dict[str, Any]:
    """
    检测人脸并保存临时图片
    用于人脸注册流程
    """
    # 解码图片
    image = decode_base64_image(base64_image)
    
    # 检测人脸
    faces = detect_faces(image)
    
    if not faces:
        return {
            "faceDetected": False,
            "faceCount": 0,
            "message": "未检测到人脸"
        }
    
    # 保存临时图片
    temp_filename = f"{uuid.uuid4().hex}.jpg"
    temp_path = config.TEMP_DIR / temp_filename
    save_base64_image(base64_image, temp_path)
    
    # 返回第一张人脸的位置
    face = faces[0]
    
    return {
        "faceDetected": True,
        "faceCount": len(faces),
        "faceLocation": {
            "top": face["top"],
            "right": face["right"],
            "bottom": face["bottom"],
            "left": face["left"]
        },
        "confidence": face["confidence"],
        "tempImage": temp_filename
    }


def register_face(employee_id: str, base64_images: List[str]) -> Dict[str, Any]:
    """
    注册员工人脸
    接收多张照片，提取人脸特征并保存
    """
    import database
    
    if not base64_images:
        return {
            "success": False,
            "message": "未提供人脸照片"
        }
    
    encodings = []
    valid_images = []
    
    for i, base64_image in enumerate(base64_images):
        # 解码图片
        image = decode_base64_image(base64_image)
        
        # 检测人脸
        faces = detect_faces(image)
        
        if not faces:
            continue
        
        # 获取人脸编码
        encoding = get_face_encoding(image, faces[0])
        
        if encoding is not None:
            encodings.append(encoding)
            valid_images.append(base64_image)
    
    if not encodings:
        return {
            "success": False,
            "message": "所有照片都未能检测到有效人脸"
        }
    
    # 计算平均编码
    avg_encoding = np.mean(encodings, axis=0)
    
    # 保存主照片
    face_filename = f"{employee_id}_{uuid.uuid4().hex[:8]}.jpg"
    face_path = config.FACES_DIR / face_filename
    save_base64_image(valid_images[0], face_path)
    
    # 序列化编码
    encoding_bytes = pickle.dumps(avg_encoding)
    
    # 更新数据库
    success = database.update_employee_face(
        employee_id=employee_id,
        face_image=face_filename,
        face_encoding=encoding_bytes
    )
    
    if success:
        return {
            "success": True,
            "message": f"成功注册人脸，使用了 {len(encodings)} 张有效照片",
            "validPhotos": len(encodings),
            "totalPhotos": len(base64_images)
        }
    else:
        return {
            "success": False,
            "message": "保存人脸数据失败"
        }


def check_in_face(base64_image: str) -> Dict[str, Any]:
    """
    人脸签到
    检测并识别人脸，完成签到
    """
    import database
    from datetime import datetime
    
    # 解码图片
    image = decode_base64_image(base64_image)
    
    # 检测人脸
    faces = detect_faces(image)
    
    if not faces:
        return {
            "success": False,
            "error": "no_face",
            "message": "未检测到人脸，请正对摄像头"
        }
    
    if len(faces) > 1:
        return {
            "success": False,
            "error": "multiple_faces",
            "message": "检测到多张人脸，请确保只有一人"
        }
    
    # 获取所有已注册人脸
    registered_employees = database.get_registered_faces()
    
    if not registered_employees:
        return {
            "success": False,
            "error": "no_registered",
            "message": "系统中没有已注册的人脸"
        }
    
    # 获取识别阈值
    settings = database.get_settings()
    threshold = settings.get("recognitionThreshold", config.DEFAULT_SETTINGS["recognition_threshold"])
    
    # 识别人脸
    result = recognize_face(image, registered_employees, threshold)
    
    if result is None or "error" in result:
        return {
            "success": False,
            "error": "not_recognized",
            "message": "未能识别身份，请重试或联系管理员"
        }
    
    # 检查是否已签到
    today = datetime.now().strftime("%Y-%m-%d")
    existing = database.get_today_attendance(result["employeeId"], today)
    
    # 记录签到
    is_check_in = existing is None  # 第一次是签到，后续是签退
    
    attendance = database.record_attendance(
        employee_id=result["employeeId"],
        is_check_in=is_check_in,
        similarity=result["similarity"]
    )
    
    return {
        "success": True,
        "type": "check_in" if is_check_in else "check_out",
        "employee": {
            "id": result["employeeId"],
            "name": result["name"],
            "department": result.get("department", ""),
            "faceImage": result.get("faceImage", "")
        },
        "similarity": result["similarity"],
        "time": attendance["time"] if attendance else datetime.now().strftime("%H:%M:%S"),
        "message": f"{'签到' if is_check_in else '签退'}成功！欢迎，{result['name']}"
    }


def detect_face_realtime(base64_image: str) -> Dict[str, Any]:
    """
    实时人脸检测（用于预览）
    返回检测到的人脸位置，不进行识别
    """
    # 解码图片
    image = decode_base64_image(base64_image)
    
    # 检测人脸
    faces = detect_faces(image)
    
    if not faces:
        return {
            "faceDetected": False,
            "faceCount": 0
        }
    
    return {
        "faceDetected": True,
        "faceCount": len(faces),
        "faces": [
            {
                "top": f["top"],
                "right": f["right"],
                "bottom": f["bottom"],
                "left": f["left"],
                "confidence": f["confidence"]
            }
            for f in faces
        ]
    }


def validate_face_quality(base64_image: str) -> Dict[str, Any]:
    """
    验证人脸照片质量
    检查亮度、清晰度、人脸大小等
    """
    # 解码图片
    image = decode_base64_image(base64_image)
    h, w = image.shape[:2]
    
    # 检测人脸
    faces = detect_faces(image)
    
    issues = []
    score = 100
    
    if not faces:
        return {
            "valid": False,
            "score": 0,
            "issues": ["未检测到人脸"]
        }
    
    if len(faces) > 1:
        issues.append("检测到多张人脸")
        score -= 30
    
    face = faces[0]
    face_width = face["right"] - face["left"]
    face_height = face["bottom"] - face["top"]
    
    # 检查人脸大小（应该占图像的合理比例）
    face_ratio = (face_width * face_height) / (w * h)
    if face_ratio < 0.05:
        issues.append("人脸太小，请靠近摄像头")
        score -= 20
    elif face_ratio > 0.8:
        issues.append("人脸太大，请稍微远离摄像头")
        score -= 10
    
    # 检查人脸位置（应该在图像中央）
    face_center_x = (face["left"] + face["right"]) / 2 / w
    face_center_y = (face["top"] + face["bottom"]) / 2 / h
    
    if abs(face_center_x - 0.5) > 0.3:
        issues.append("请将人脸移到画面中央")
        score -= 15
    
    if abs(face_center_y - 0.5) > 0.3:
        issues.append("请将人脸移到画面中央")
        score -= 15
    
    # 检查图像亮度
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    
    if brightness < 50:
        issues.append("光线太暗，请增加照明")
        score -= 20
    elif brightness > 200:
        issues.append("光线太亮，请避免强光直射")
        score -= 15
    
    # 检查图像清晰度（拉普拉斯方差）
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 100:
        issues.append("图像模糊，请保持稳定")
        score -= 20
    
    score = max(0, score)
    
    return {
        "valid": score >= 60 and len([i for i in issues if "未检测" in i or "多张" in i]) == 0,
        "score": score,
        "issues": issues,
        "faceLocation": {
            "top": face["top"],
            "right": face["right"],
            "bottom": face["bottom"],
            "left": face["left"]
        },
        "confidence": face["confidence"]
    }


def delete_face(employee_id: str) -> Dict[str, Any]:
    """
    删除员工人脸数据
    """
    import database
    
    # 获取员工信息
    employee = database.get_employee(employee_id)
    
    if not employee:
        return {
            "success": False,
            "message": "员工不存在"
        }
    
    # 删除人脸图片文件
    if employee.get("faceImage"):
        face_path = config.FACES_DIR / employee["faceImage"]
        if face_path.exists():
            try:
                face_path.unlink()
            except:
                pass
    
    # 更新数据库
    success = database.update_employee_face(
        employee_id=employee_id,
        face_image=None,
        face_encoding=None
    )
    
    return {
        "success": success,
        "message": "人脸数据已删除" if success else "删除失败"
    }


def process_attendance(base64_image: str, attendance_type: str = "check_in") -> Dict[str, Any]:
    """
    处理考勤（签到/签退）
    attendance_type: "check_in" 或 "check_out"
    """
    import database
    from datetime import datetime
    
    # 解码图片
    image = decode_base64_image(base64_image)
    
    # 检测人脸
    faces = detect_faces(image)
    
    if not faces:
        return {
            "success": False,
            "error": "no_face",
            "message": "未检测到人脸，请正对摄像头"
        }
    
    if len(faces) > 1:
        return {
            "success": False,
            "error": "multiple_faces",
            "message": "检测到多张人脸，请确保只有一人"
        }
    
    # 获取所有已注册人脸
    registered_employees = database.get_registered_faces()
    
    if not registered_employees:
        return {
            "success": False,
            "error": "no_registered",
            "message": "系统中没有已注册的人脸"
        }
    
    # 获取识别阈值
    settings = database.get_settings()
    threshold = settings.get("recognitionThreshold", config.DEFAULT_SETTINGS["recognition_threshold"])
    
    # 识别人脸
    result = recognize_face(image, registered_employees, threshold)
    
    if result is None or "error" in result:
        return {
            "success": False,
            "error": "not_recognized",
            "message": "未能识别身份，请重试或联系管理员"
        }
    
    # 记录考勤
    is_check_in = attendance_type == "check_in"
    
    attendance = database.record_attendance(
        employee_id=result["employeeId"],
        is_check_in=is_check_in,
        similarity=result["similarity"]
    )
    
    current_time = attendance["time"] if attendance else datetime.now().strftime("%H:%M:%S")
    # database.record_attendance 已经返回中文状态，直接使用
    status = attendance.get("status", "正常") if attendance else "正常"
    
    # 返回格式与前端期望一致
    return {
        "success": True,
        "type": attendance_type,
        "employeeId": result["employeeId"],
        "name": result["name"],
        "department": result.get("department", ""),
        "faceImage": result.get("faceImage", ""),
        "similarity": result["similarity"],
        "checkInTime": current_time if is_check_in else None,
        "checkOutTime": current_time if not is_check_in else None,
        "time": current_time,
        "status": status,  # 已经是中文状态
        "message": f"{'签到' if is_check_in else '签退'}成功！欢迎，{result['name']}"
    }
