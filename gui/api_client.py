"""
API客户端模块
封装所有HTTP请求到后端API
"""
import requests
from typing import Optional, Dict, List, Any
from .config import config
from .utils.token_manager import token_manager

class APIError(Exception):
    """API请求异常"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class APIClient:
    """API客户端类"""
    
    def __init__(self):
        self.base_url = config.api_base_url
        self.timeout = config.api_timeout
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法（GET, POST, PUT, DELETE等）
            endpoint: API端点路径
            data: 请求数据（JSON）
            files: 文件上传数据
            require_auth: 是否需要认证
        
        Returns:
            响应数据字典
        
        Raises:
            APIError: API请求失败
        """
        url = config.get_api_url(endpoint)
        headers = {"Content-Type": "application/json"}
        
        # 添加认证头
        if require_auth:
            auth_header = token_manager.get_auth_header()
            if auth_header:
                headers.update(auth_header)
            else:
                raise APIError("未登录或Token已过期，请重新登录", 401)
        
        # 文件上传时不设置Content-Type，让requests自动处理
        if files:
            headers.pop("Content-Type", None)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=self.timeout)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files, timeout=self.timeout)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=self.timeout)
            else:
                raise APIError(f"不支持的HTTP方法: {method}")
            
            # 检查响应状态
            if response.status_code >= 400:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error") or error_data.get("message") or response.text or f"HTTP {response.status_code}"
                raise APIError(error_msg, response.status_code)
            
            # 返回响应数据
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text}
        
        except requests.exceptions.Timeout:
            raise APIError("请求超时，请检查网络连接", 408)
        except requests.exceptions.ConnectionError:
            raise APIError(f"无法连接到服务器 {self.base_url}，请确保后端服务已启动", 503)
        except requests.exceptions.RequestException as e:
            raise APIError(f"请求失败: {str(e)}", None)
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"未知错误: {str(e)}", None)
    
    # ==================== 用户相关API ====================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        本地账号登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            包含access_token的响应数据
        """
        data = {
            "username": username,
            "password": password
        }
        response = self._make_request("POST", "/api/user/login", data=data, require_auth=False)
        
        # 保存Token
        if "access_token" in response:
            token_manager.save_token(response["access_token"], expires_in=1800)  # 30分钟
        
        return response
    
    def login_cas(self, cas_username: str, cas_password: str) -> Dict[str, Any]:
        """
        CAS登录
        
        Args:
            cas_username: CAS用户名（学号）
            cas_password: CAS密码
        
        Returns:
            包含access_token和用户信息的响应数据
        """
        data = {
            "cas_username": cas_username,
            "cas_password": cas_password
        }
        response = self._make_request("POST", "/api/user/login/cas", data=data, require_auth=False)
        
        # 保存Token
        if "access_token" in response:
            token_manager.save_token(response["access_token"], expires_in=1800)  # 30分钟
        
        return response
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            用户信息
        """
        return self._make_request("GET", "/api/user/me")
    
    def logout(self) -> Dict[str, Any]:
        """
        登出
        
        Returns:
            登出响应
        """
        try:
            response = self._make_request("POST", "/api/user/logout")
        finally:
            # 无论API调用是否成功，都清除本地Token
            token_manager.clear_token()
        return response
    
    # ==================== 作业相关API ====================
    
    def get_assignments(self) -> List[Dict[str, Any]]:
        """
        获取当前用户的所有作业
        
        Returns:
            作业列表
        """
        response = self._make_request("GET", "/api/assignment/")
        return response.get("data", [])
    
    def sync_assignments(self, school_username: str, school_password: str) -> Dict[str, Any]:
        """
        同步作业（从学校系统抓取）
        
        Args:
            school_username: 学校账号（学号）
            school_password: 学校密码
        
        Returns:
            同步结果（包含新增和更新数量）
        """
        data = {
            "school_username": school_username,
            "school_password": school_password
        }
        return self._make_request("POST", "/api/assignment/sync", data=data)
    
    def submit_assignment(self, assignment_id: int, file_path: str) -> Dict[str, Any]:
        """
        提交作业文件
        
        Args:
            assignment_id: 作业ID
            file_path: 文件路径
        
        Returns:
            提交结果
        
        Note:
            如果后端还没有实现此接口，此方法会抛出APIError
        """
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_path.split('/')[-1], f, 'application/zip')
                }
                data = {
                    'assignment_id': assignment_id
                }
                return self._make_request("POST", f"/api/assignment/{assignment_id}/submit", data=data, files=files)
        except FileNotFoundError:
            raise APIError(f"文件不存在: {file_path}")
        except Exception as e:
            raise APIError(f"读取文件失败: {str(e)}")

# 全局API客户端实例
api_client = APIClient()


