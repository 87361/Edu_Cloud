import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from werkzeug.exceptions import HTTPException

from src.edu_cloud.common.config import settings
from src.edu_cloud.common.database import engine, Base
from src.edu_cloud.user.api import user_bp

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
    
    # 配置CORS - 更灵活的配置
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["*"],  # 在生产环境中应该限制具体域名
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "expose_headers": ["X-Total-Count"],
                 "supports_credentials": True
             }
         })
    
    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
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
    app.run(host='0.0.0.0', port=5000, debug=True)
