# 验证脚本：test_imports.py
import fastapi
import sqlalchemy
import pymysql
import jose
import passlib
import onnxruntime
import cv2
import numpy
from PIL import Image

print("✅ 所有核心依赖包导入成功！")
print(f"FastAPI 版本：{fastapi.__version__}")
print(f"SQLAlchemy 版本：{sqlalchemy.__version__}")
print(f"ONNX Runtime 版本：{onnxruntime.__version__}")
print(f"OpenCV 版本：{cv2.__version__}")