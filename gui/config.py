"""
配置管理模块
读取API地址等配置信息
"""
import os
import json
from pathlib import Path
from typing import Optional

class Config:
    """应用配置类"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".edu_cloud_gui"
        self.config_file = self.config_dir / "config.json"
        self.token_file = self.config_dir / "token.txt"
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 默认配置
        self.api_base_url = os.getenv("EDU_CLOUD_API_URL", "http://localhost:5000")
        self.api_timeout = 30  # 请求超时时间（秒）
        
        # 从配置文件加载
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.api_base_url = config_data.get("api_base_url", self.api_base_url)
                    self.api_timeout = config_data.get("api_timeout", self.api_timeout)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                "api_base_url": self.api_base_url,
                "api_timeout": self.api_timeout
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_api_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        # 确保endpoint以/开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"{self.api_base_url}{endpoint}"
    
    def get_token_path(self) -> Path:
        """获取Token文件路径"""
        return self.token_file

# 全局配置实例
config = Config()

