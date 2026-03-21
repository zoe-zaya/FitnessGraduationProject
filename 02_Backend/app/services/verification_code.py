"""
验证码服务
实现验证码生成、发送、验证功能
对应《需求规格说明书》3.2 节忘记密码用例
"""

import random
import time
from typing import Dict, Optional
from datetime import datetime, timedelta


class VerificationCodeService:
    """
    验证码服务类
    开发环境使用内存存储，生产环境应使用 Redis
    """
    
    # 内存存储验证码（开发环境）
    # 格式：{phone: {"code": "123456", "expire_time": datetime, "verified": False}}
    _codes: Dict[str, dict] = {}
    
    # 验证码有效期（秒）
    CODE_EXPIRE_SECONDS = 300  # 5 分钟
    
    # 验证码长度
    CODE_LENGTH = 6
    
    # 发送间隔（秒）
    SEND_INTERVAL_SECONDS = 60
    
    # 最大尝试次数
    MAX_VERIFY_ATTEMPTS = 5
    
    @classmethod
    def generate_code(cls) -> str:
        """生成 6 位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(cls.CODE_LENGTH)])
    
    @classmethod
    def send_code(cls, phone: str) -> dict:
        """
        发送验证码
        对应《需求规格说明书》3.2 节忘记密码用例步骤 3-4
        
        Args:
            phone: 手机号
            
        Returns:
            dict: {"message": str, "expire_seconds": int}
        """
        # 检查发送间隔
        if phone in cls._codes:
            last_send_time = cls._codes[phone].get("last_send_time")
            if last_send_time:
                elapsed = (datetime.now() - last_send_time).total_seconds()
                if elapsed < cls.SEND_INTERVAL_SECONDS:
                    wait_time = int(cls.SEND_INTERVAL_SECONDS - elapsed)
                    return {
                        "success": False,
                        "message": f"验证码已发送，请{wait_time}秒后再试",
                        "wait_seconds": wait_time
                    }
        
        # 生成验证码
        code = cls.generate_code()
        expire_time = datetime.now() + timedelta(seconds=cls.CODE_EXPIRE_SECONDS)
        
        # 存储验证码（开发环境打印到控制台）
        cls._codes[phone] = {
            "code": code,
            "expire_time": expire_time,
            "verified": False,
            "attempts": 0,
            "last_send_time": datetime.now()
        }
        
        # 开发环境：打印验证码到控制台
        print(f"\n{'='*50}")
        print(f"【验证码服务】手机号：{phone}")
        print(f"【验证码服务】验证码：{code}")
        print(f"【验证码服务】有效期：{cls.CODE_EXPIRE_SECONDS}秒")
        print(f"{'='*50}\n")
        
        # 生产环境应调用短信服务
        # await sms_service.send(phone, code)
        
        return {
            "success": True,
            "message": "验证码已发送",
            "expire_seconds": cls.CODE_EXPIRE_SECONDS
        }
    
    @classmethod
    def verify_code(cls, phone: str, code: str) -> dict:
        """
        验证验证码
        对应《需求规格说明书》3.2 节忘记密码用例步骤 4
        
        Args:
            phone: 手机号
            code: 验证码
            
        Returns:
            dict: {"is_valid": bool, "message": str}
        """
        # 检查验证码是否存在
        if phone not in cls._codes:
            return {
                "is_valid": False,
                "message": "验证码不存在，请先获取验证码"
            }
        
        code_info = cls._codes[phone]
        
        # 检查是否已验证
        if code_info.get("verified"):
            return {
                "is_valid": False,
                "message": "验证码已使用，请重新获取"
            }
        
        # 检查尝试次数
        if code_info.get("attempts", 0) >= cls.MAX_VERIFY_ATTEMPTS:
            # 超过最大尝试次数，删除验证码
            del cls._codes[phone]
            return {
                "is_valid": False,
                "message": "验证次数过多，请重新获取验证码"
            }
        
        # 检查是否过期
        if datetime.now() > code_info["expire_time"]:
            del cls._codes[phone]
            return {
                "is_valid": False,
                "message": "验证码已过期，请重新获取"
            }
        
        # 验证验证码
        code_info["attempts"] = code_info.get("attempts", 0) + 1
        
        if code != code_info["code"]:
            remaining = cls.MAX_VERIFY_ATTEMPTS - code_info["attempts"]
            return {
                "is_valid": False,
                "message": f"验证码错误，剩余{remaining}次尝试机会"
            }
        
        # 验证成功，标记为已验证
        code_info["verified"] = True
        
        return {
            "is_valid": True,
            "message": "验证码验证成功"
        }
    
    @classmethod
    def clear_code(cls, phone: str):
        """清除验证码（重置密码成功后调用）"""
        if phone in cls._codes:
            del cls._codes[phone]
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的验证码（可定期调用）"""
        now = datetime.now()
        expired_phones = [
            phone for phone, info in cls._codes.items()
            if now > info["expire_time"]
        ]
        for phone in expired_phones:
            del cls._codes[phone]