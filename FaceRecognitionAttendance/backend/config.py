"""
人脸签到考勤系统 - 配置文件
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_PATH = BASE_DIR / "data" / "attendance.db"

# 上传文件配置
UPLOAD_DIR = BASE_DIR / "uploads"
FACES_DIR = UPLOAD_DIR / "faces"
TEMP_DIR = UPLOAD_DIR / "temp"

# 确保目录存在
UPLOAD_DIR.mkdir(exist_ok=True)
FACES_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
(BASE_DIR / "data").mkdir(exist_ok=True)

# 服务器配置
HOST = "0.0.0.0"
PORT = 8081

# 考勤默认设置
DEFAULT_SETTINGS = {
    "work_start_time": "09:00",
    "work_end_time": "18:00",
    "late_threshold": 10,      # 迟到容忍时间（分钟）
    "early_threshold": 10,     # 早退容忍时间（分钟）
    "recognition_threshold": 0.5,  # 人脸识别阈值（越小越严格）
}

# 人脸识别配置
FACE_RECOGNITION_MODEL = "hog"  # 可选 "hog"（快）或 "cnn"（准确但需要GPU）
FACE_ENCODING_NUM_JITTERS = 1   # 编码时的抖动次数，越大越准确但更慢

# 图片配置
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 最大图片大小 2MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
