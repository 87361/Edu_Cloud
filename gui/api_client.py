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
    
    def get_cas_status(self) -> Dict[str, Any]:
        """
        获取当前用户的CAS绑定状态
        
        Returns:
            CAS绑定状态信息
        """
        response = self._make_request("GET", "/api/user/me/cas-status")
        return response.get("data", {})
    
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
    
    def sync_assignments(self, school_username: str = None, school_password: str = None, cas_password: str = None) -> Dict[str, Any]:
        """
        同步作业（从学校系统抓取）
        
        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）
        
        Returns:
            同步结果（包含新增和更新数量）
        """
        data = {}
        if school_username:
            data["school_username"] = school_username
        if school_password:
            data["school_password"] = school_password
        if cas_password:
            data["cas_password"] = cas_password
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
    
    # ==================== 课程相关API ====================
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        获取当前用户的课程列表
        
        Returns:
            课程列表
        """
        response = self._make_request("GET", "/api/course/")
        return response.get("data", [])
    
    def get_course_detail(self, course_id: int) -> Dict[str, Any]:
        """
        获取课程详情
        
        Args:
            course_id: 课程ID
        
        Returns:
            课程详情
        """
        response = self._make_request("GET", f"/api/course/{course_id}")
        return response.get("data", {})
    
    def get_course_resources(self, course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程资源列表
        
        Args:
            course_id: 课程ID
        
        Returns:
            资源列表
        """
        response = self._make_request("GET", f"/api/course/{course_id}/resources")
        return response.get("data", [])
    
    def sync_courses(self, school_username: str = None, school_password: str = None, cas_password: str = None) -> Dict[str, Any]:
        """
        同步课程（从学校系统抓取）
        
        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）
        
        Returns:
            同步结果
        """
        data = {}
        if school_username:
            data["school_username"] = school_username
        if school_password:
            data["school_password"] = school_password
        if cas_password:
            data["cas_password"] = cas_password
        return self._make_request("POST", "/api/course/sync", data=data)
    
    # ==================== 讨论相关API ====================
    
    def get_course_discussions(self, course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程讨论列表
        
        Args:
            course_id: 课程ID
        
        Returns:
            讨论列表
        """
        response = self._make_request("GET", "/api/discussion/list", data={"course_id": course_id})
        return response.get("data", [])
    
    def get_discussion_detail(self, topic_id: int) -> Dict[str, Any]:
        """
        获取讨论详情和回复
        
        Args:
            topic_id: 讨论主题ID
        
        Returns:
            讨论详情和回复列表
        """
        response = self._make_request("GET", f"/api/discussion/{topic_id}")
        return response.get("data", {})
    
    def sync_discussions(self, school_username: str = None, school_password: str = None, cas_password: str = None) -> Dict[str, Any]:
        """
        同步讨论（从学校系统抓取）
        
        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）
        
        Returns:
            同步结果
        """
        data = {}
        if school_username:
            data["school_username"] = school_username
        if school_password:
            data["school_password"] = school_password
        if cas_password:
            data["cas_password"] = cas_password
        return self._make_request("POST", "/api/discussion/sync", data=data)
    
    # ==================== 公告相关API ====================
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """
        获取公告列表
        
        Returns:
            公告列表
        """
        response = self._make_request("GET", "/api/notification/")
        return response.get("data", [])
    
    def sync_notifications(self, school_username: str = None, school_password: str = None, cas_password: str = None) -> Dict[str, Any]:
        """
        同步公告（从学校系统抓取）
        
        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）
        
        Returns:
            同步结果
        """
        data = {}
        if school_username:
            data["school_username"] = school_username
        if school_password:
            data["school_password"] = school_password
        if cas_password:
            data["cas_password"] = cas_password
        return self._make_request("POST", "/api/notification/sync", data=data)
    
    # ==================== 管理员相关API ====================
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """
        获取管理员统计信息
        
        Returns:
            统计信息
        """
        response = self._make_request("GET", "/api/admin/database/stats")
        return response.get("data", {})
    
    def get_admin_users(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        role: Optional[str] = None, 
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        获取用户列表（管理员）
        
        Args:
            limit: 返回记录数
            offset: 偏移量
            role: 按角色筛选（'user' 或 'admin'）
            is_active: 按活跃状态筛选
        
        Returns:
            用户列表和总数
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if role:
            params["role"] = role
        if is_active is not None:
            params["is_active"] = "true" if is_active else "false"
        
        # GET请求使用params参数（query string），不是data（body）
        response = self._make_request("GET", "/api/admin/users", data=params)
        return response.get("data", {})
    
    def get_admin_database_tables(self) -> Dict[str, Any]:
        """
        获取数据库表列表（管理员）
        
        Returns:
            表列表和结构信息
        """
        response = self._make_request("GET", "/api/admin/database/tables")
        return response.get("data", {})
    
    def get_admin_table_data(
        self, 
        table_name: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取表数据（管理员）
        
        Args:
            table_name: 表名
            limit: 返回记录数
            offset: 偏移量
        
        Returns:
            表数据
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        # GET请求使用params参数（query string），不是data（body）
        response = self._make_request("GET", f"/api/admin/database/table/{table_name}", data=params)
        return response.get("data", {})

# 全局API客户端实例
api_client = APIClient()


