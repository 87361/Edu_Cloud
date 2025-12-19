"""CAS 认证工具模块"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from buptmw import BUPT_Auth
from .security import get_password_hash, verify_password


def verify_cas_credentials(cas_username: str, cas_password: str) -> Tuple[bool, Optional[BUPT_Auth], Optional[str]]:
    """
    验证 CAS 凭证
    
    Args:
        cas_username: CAS 用户名（学号）
        cas_password: CAS 密码
        
    Returns:
        (is_valid, auth_object, error_message)
        - is_valid: 凭证是否有效
        - auth_object: 如果有效，返回 BUPT_Auth 对象；否则为 None
        - error_message: 如果无效，返回错误信息；否则为 None
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 记录调试信息（不记录完整密码，只记录长度和首尾字符）
        password_preview = f"{cas_password[0] if cas_password else ''}***{cas_password[-1] if len(cas_password) > 1 else ''}" if cas_password else "空"
        logger.debug(f"尝试 CAS 认证 - 用户名: {cas_username}, 密码长度: {len(cas_password) if cas_password else 0}")
        
        auth = BUPT_Auth(cas={"username": cas_username, "password": cas_password})
        
        # 检查 CAS 认证状态
        if not hasattr(auth, 'cas') or not hasattr(auth.cas, 'status'):
            return False, None, "CAS 认证失败：无法获取认证状态"
        
        if auth.cas.status is not True:
            # 尝试获取更详细的错误信息
            error_detail = "用户名或密码错误"
            if hasattr(auth.cas, 'message'):
                error_detail = auth.cas.message
            elif hasattr(auth.cas, 'error'):
                error_detail = auth.cas.error
            
            # 检查是否是账户锁定
            if "423" in str(auth.cas.status) or "Locked" in str(error_detail):
                return False, None, "CAS 认证失败：账户已被锁定，请稍后再试"
            
            return False, None, f"CAS 认证失败：{error_detail}"
        
        return True, auth, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"CAS 认证异常: {error_msg}")
        
        # 检查是否是账户锁定错误
        if "423" in error_msg or "Locked" in error_msg:
            return False, None, "CAS 认证失败：账户已被锁定，请稍后再试"
        
        # 检查是否是401错误
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, None, "CAS 认证失败：用户名或密码错误"
        
        return False, None, f"CAS 认证错误：{error_msg}"


def encrypt_cas_password(cas_password: str) -> str:
    """
    加密 CAS 密码（使用与用户密码相同的加密方式）
    
    Args:
        cas_password: 原始 CAS 密码
        
    Returns:
        加密后的密码
    """
    return get_password_hash(cas_password)


def verify_cas_password(plain_password: str, encrypted_password: str) -> bool:
    """
    验证 CAS 密码
    
    Args:
        plain_password: 原始密码
        encrypted_password: 加密后的密码
        
    Returns:
        密码是否正确
    """
    return verify_password(plain_password, encrypted_password)


def get_cas_auth_object(cas_username: str, cas_password_encrypted: str, plain_password: str) -> Optional[BUPT_Auth]:
    """
    从加密密码获取 BUPT_Auth 对象
    
    注意：此函数需要传入明文密码，因为 BUPT_Auth 需要明文密码进行认证
    
    Args:
        cas_username: CAS 用户名
        cas_password_encrypted: 加密的 CAS 密码（用于验证）
        plain_password: 明文密码（用于创建 BUPT_Auth 对象）
        
    Returns:
        BUPT_Auth 对象，如果密码验证失败则返回 None
    """
    # 验证密码
    if not verify_cas_password(plain_password, cas_password_encrypted):
        return None
    
    # 创建并验证 BUPT_Auth 对象
    is_valid, auth_object, _ = verify_cas_credentials(cas_username, plain_password)
    if is_valid:
        return auth_object
    
    return None

