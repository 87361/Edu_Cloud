import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from werkzeug.exceptions import HTTPException

from src.edu_cloud.common.config import settings
from src.edu_cloud.common.database import engine, Base, SessionLocal
from src.edu_cloud.common.token_manager import is_token_revoked
from src.edu_cloud.user.api import user_bp
# 导入模型以确保表被创建
from src.edu_cloud.user import models  # 这会导入User和TokenBlacklist模型

from src.edu_cloud.course.api import course_bp 
from src.edu_cloud.discussion.api import discussion_bp
from src.edu_cloud.notification.api import notification_bp


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建Flask应用
def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = settings.secret_key
    app.config['JWT_SECRET_KEY'] = settings.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = settings.access_token_expire_minutes * 60  # 转换为秒
    app.config['JSON_SORT_KEYS'] = False  # 保持JSON字段顺序
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # Token黑名单检查回调
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """
        检查token是否已被撤销
        这个回调函数会在每次验证token时被调用
        """
        jti = jwt_payload.get("jti")
        if not jti:
            return True  # 如果没有JTI，认为token无效
        
        db = SessionLocal()
        try:
            return is_token_revoked(db, jti)
        except Exception as e:
            logger.error(f"Error checking token revocation: {str(e)}")
            return True  # 发生错误时，为了安全起见，认为token已被撤销
        finally:
            db.close()
    
    # 配置CORS - 支持环境变量配置
    cors_origins = settings.cors_origins.split(",") if "," in settings.cors_origins else [settings.cors_origins]
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": cors_origins,  # 从配置读取，生产环境应限制具体域名
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "expose_headers": ["X-Total-Count"],
                 "supports_credentials": settings.cors_supports_credentials
             }
         })
    
    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/user') 
    
    from src.edu_cloud.assignment.api import assignment_bp
    # 注册assignment
    app.register_blueprint(assignment_bp, url_prefix='/api/assignment')
    
    from src.edu_cloud.admin.api import admin_bp
    # 注册管理员API
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # 2. 注册 blueprint
    app.register_blueprint(course_bp, url_prefix='/api/course')
    app.register_blueprint(discussion_bp, url_prefix='/api/discussion')
    app.register_blueprint(notification_bp, url_prefix='/api/notification')
    
    # 根路径
    @app.route('/')
    def root():
        return jsonify({
            "message": "Welcome to Edu Cloud API",
            "version": "1.0.0",
            "endpoints": {
                "users": "/api/user",
                "docs": "/docs"
            }
        })
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "edu-cloud-api"
        })
    
    # 全局错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad request",
            "message": str(error.description) if hasattr(error, 'description') else "The request is invalid"
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication is required"
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "message": "You don't have permission to access this resource"
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "message": "The HTTP method is not allowed for this endpoint"
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token expired",
            "message": "The access token has expired"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "Invalid token",
            "message": "The access token is invalid"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Missing token",
            "message": "Authorization token is required"
        }), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Fresh token required",
            "message": "A fresh token is required for this endpoint"
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token revoked",
            "message": "The token has been revoked"
        }), 401
    
    # 请求日志中间件
    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def log_response_info(response):
        logger.info(f"Response: {response.status_code} {request.method} {request.path}")
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
