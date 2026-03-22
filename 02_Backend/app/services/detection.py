"""
器材检测服务
调用 YOLOv5 模型进行健身器材识别
对应《任务书》技术指标：准确率≥85%，响应时间<2 秒
"""

import onnxruntime as ort
import numpy as np
import cv2
import time
from typing import List, Dict
from app.core.config import settings


class EquipmentDetector:
    """
    健身器材检测器
    使用 ONNX Runtime 加速推理
    """
    
    def __init__(self):
        """初始化检测器，加载模型"""
        try:
            self.session = ort.InferenceSession(
                settings.MODEL_PATH,
                providers=['CPUExecutionProvider']  # 如有 GPU 可改为 'CUDAExecutionProvider'
            )
            self.input_name = self.session.get_inputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape
            self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        except Exception as e:
            print(f"模型加载失败：{e}")
            raise
    
    def preprocess(self, image_bytes: bytes) -> tuple:
        """
        图像预处理
        1. 解码图片
        2. Resize 至 640x640
        3. 归一化
        4. 转换为 CHW 格式
        """
        # 1. 解码图片
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("图片解码失败")
        
        # 2. 保存原始尺寸用于坐标还原
        original_shape = image.shape[:2]  # (height, width)
        
        # 3. Resize 至模型输入尺寸
        input_size = (640, 640)
        resized = cv2.resize(image, input_size)
        
        # 4. 归一化 (0-255 -> 0-1)
        normalized = resized.astype(np.float32) / 255.0
        
        # 5. 转换为 CHW 格式并添加 batch 维度
        transposed = np.transpose(normalized, (2, 0, 1))
        batched = np.expand_dims(transposed, axis=0)
        
        return batched, original_shape
    
    def postprocess(self, outputs: List[np.ndarray], original_shape: tuple) -> List[Dict]:
        """
        后处理
        1. 解析模型输出
        2. 过滤低置信度结果
        3. 还原坐标至原始图片尺寸
        """
        results = []
        
        # YOLOv5 输出格式：[batch, num_boxes, 85]
        # 85 = 4 (坐标) + 1 (置信度) + 80 (类别)
        output = outputs[0][0]  # 取第一个 batch
        
        for detection in output:
            confidence = float(detection[4])
            
            # 过滤低置信度（《需求规格说明书》2.2.3 业务规则）
            if confidence < self.confidence_threshold:
                continue
            
            # 获取类别（简化处理，假设单类别）
            class_scores = detection[5:]
            class_id = int(np.argmax(class_scores))
            
            # 获取坐标 (x_center, y_center, width, height)
            x_center = float(detection[0])
            y_center = float(detection[1])
            width = float(detection[2])
            height = float(detection[3])
            
            # 转换为左上角坐标
            x1 = (x_center - width / 2) / 640 * original_shape[1]
            y1 = (y_center - height / 2) / 640 * original_shape[0]
            x2 = (x_center + width / 2) / 640 * original_shape[1]
            y2 = (y_center + height / 2) / 640 * original_shape[0]
            
            # 映射类别 ID 到器材 ID（需根据实际模型调整）
            equipment_id = f"equipment_{class_id}"
            
            results.append({
                'equipment_id': equipment_id,
                'confidence': confidence,
                'box': [x1, y1, x2, y2]
            })
        
        return results
    
    def detect(self, image_bytes: bytes) -> List[Dict]:
        """
        执行检测
        对应《需求规格说明书》2.2.3 detectFromImage() 函数
        
        流程：
        1. 预处理
        2. 推理
        3. 后处理
        4. 返回结果
        """
        start_time = time.time()
        
        try:
            # 1. 预处理
            input_data, original_shape = self.preprocess(image_bytes)
            
            # 2. 推理
            outputs = self.session.run(None, {self.input_name: input_data})
            
            # 3. 后处理
            results = self.postprocess(outputs, original_shape)
            
            # 4. 记录耗时
            detection_time = time.time() - start_time
            
            # 5. 验证响应时间（《任务书》要求<2 秒）
            if detection_time > 2.0:
                print(f"警告：检测耗时{detection_time:.2f}秒，超过 2 秒限制")
            
            return results
            
        except Exception as e:
            print(f"检测失败：{e}")
            return []