"""
Token管理器
处理JWT Token的存储、读取和验证
"""
import json
import time
from pathlib import Path
from typing import Optional
from ..config import config

class TokenManager:
    """JWT Token管理器"""
    
    def __init__(self):
        self.token_file = config.get_token_path()
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
    
    def save_token(self, token: str, expires_in: int = 1800):
        """
        保存Token到文件
        
        Args:
            token: JWT Token字符串
            expires_in: Token有效期（秒），默认30分钟
        """
        self._token = token
        self._token_expires_at = time.time() + expires_in
        
        try:
            token_data = {
                "token": token,
                "expires_at": self._token_expires_at
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"保存Token失败: {e}")
    
    def load_token(self) -> Optional[str]:
        """从文件加载Token"""
        if self._token:
            # 如果内存中有token，先检查是否过期
            if self.is_token_valid():
                return self._token
        
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                self._token = token_data.get("token")
                self._token_expires_at = token_data.get("expires_at")
                
                if self.is_token_valid():
                    return self._token
                else:
                    # Token已过期，清除
                    self.clear_token()
                    return None
        except Exception as e:
            print(f"加载Token失败: {e}")
            return None
    
    def get_token(self) -> Optional[str]:
        """获取当前Token（如果有效）"""
        if not self._token:
            self._token = self.load_token()
        return self._token if self.is_token_valid() else None
    
    def is_token_valid(self) -> bool:
        """检查Token是否有效（未过期）"""
        if not self._token:
            return False
        
        if self._token_expires_at is None:
            # 如果没有过期时间，假设有效（向后兼容）
            return True
        
        # 提前5分钟认为过期，避免在请求时过期
        return time.time() < (self._token_expires_at - 300)
    
    def clear_token(self):
        """清除Token"""
        self._token = None
        self._token_expires_at = None
        
        if self.token_file.exists():
            try:
                self.token_file.unlink()
            except Exception as e:
                print(f"删除Token文件失败: {e}")
    
    def get_auth_header(self) -> Optional[dict]:
        """获取Authorization请求头"""
        token = self.get_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return None

# 全局Token管理器实例
token_manager = TokenManager()


