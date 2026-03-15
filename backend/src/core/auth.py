"""
认证授权模块
JWT + RBAC
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from functools import wraps

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 安全认证
security = HTTPBearer()


# ==================== 数据模型 ====================

class TokenData(BaseModel):
    """Token数据"""
    user_id: str
    username: str
    role: str


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserCreate(BaseModel):
    """创建用户"""
    username: str
    email: str
    password: str
    full_name: str = ""
    role: str = "viewer"


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


# ==================== 权限定义 ====================

class Permission(str, Enum):
    """权限枚举"""
    # 告警权限
    ALERT_VIEW = "alert:view"
    ALERT_EDIT = "alert:edit"
    ALERT_DELETE = "alert:delete"
    
    # 事件权限
    INCIDENT_VIEW = "incident:view"
    INCIDENT_EDIT = "incident:edit"
    INCIDENT_CLOSE = "incident:close"
    
    # 资产权限
    ASSET_VIEW = "asset:view"
    ASSET_EDIT = "asset:edit"
    ASSET_DELETE = "asset:delete"
    
    # 操作权限
    ACTION_VIEW = "action:view"
    ACTION_EXECUTE = "action:execute"
    ACTION_APPROVE = "action:approve"
    
    # 报表权限
    REPORT_VIEW = "report:view"
    REPORT_GENERATE = "report:generate"
    
    # 用户权限
    USER_VIEW = "user:view"
    USER_EDIT = "user:edit"
    USER_ADMIN = "user:admin"
    
    # 系统权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_AUDIT = "system:audit"


# 角色权限映射
ROLE_PERMISSIONS = {
    "admin": [
        Permission.ALERT_VIEW, Permission.ALERT_EDIT, Permission.ALERT_DELETE,
        Permission.INCIDENT_VIEW, Permission.INCIDENT_EDIT, Permission.INCIDENT_CLOSE,
        Permission.ASSET_VIEW, Permission.ASSET_EDIT, Permission.ASSET_DELETE,
        Permission.ACTION_VIEW, Permission.ACTION_EXECUTE, Permission.ACTION_APPROVE,
        Permission.REPORT_VIEW, Permission.REPORT_GENERATE,
        Permission.USER_VIEW, Permission.USER_EDIT, Permission.USER_ADMIN,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_AUDIT
    ],
    "analyst": [
        Permission.ALERT_VIEW, Permission.ALERT_EDIT,
        Permission.INCIDENT_VIEW, Permission.INCIDENT_EDIT,
        Permission.ASSET_VIEW,
        Permission.ACTION_VIEW, Permission.ACTION_EXECUTE, Permission.ACTION_APPROVE,
        Permission.REPORT_VIEW, Permission.REPORT_GENERATE,
        Permission.SYSTEM_AUDIT
    ],
    "viewer": [
        Permission.ALERT_VIEW,
        Permission.INCIDENT_VIEW,
        Permission.ASSET_VIEW,
        Permission.ACTION_VIEW,
        Permission.REPORT_VIEW
    ]
}


from enum import Enum


# ==================== 认证服务 ====================

class AuthService:
    """认证服务"""
    
    def __init__(self):
        # 模拟用户存储（实际应从数据库读取）
        self._users = {
            "admin": {
                "id": "user-001",
                "username": "admin",
                "email": "admin@aisecops.local",
                "password": pwd_context.hash("admin123"),
                "full_name": "系统管理员",
                "role": "admin",
                "is_active": True
            },
            "analyst": {
                "id": "user-002",
                "username": "analyst",
                "email": "analyst@aisecops.local",
                "password": pwd_context.hash("analyst123"),
                "full_name": "安全分析师",
                "role": "analyst",
                "is_active": True
            },
            "viewer": {
                "id": "user-003",
                "username": "viewer",
                "email": "viewer@aisecops.local",
                "password": pwd_context.hash("viewer123"),
                "full_name": "查看用户",
                "role": "viewer",
                "is_active": True
            }
        }
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user(self, username: str) -> Optional[dict]:
        """获取用户"""
        return self._users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """认证用户"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user["password"]):
            return None
        return user
    
    def create_access_token(self, user: dict) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("user_id")
            username: str = payload.get("username")
            role: str = payload.get("role")
            
            if user_id is None or username is None:
                return None
            
            return TokenData(user_id=user_id, username=username, role=role)
        except JWTError:
            return None
    
    def get_user_permissions(self, role: str) -> List[Permission]:
        """获取用户权限"""
        return ROLE_PERMISSIONS.get(role, [])
    
    def has_permission(self, role: str, permission: Permission) -> bool:
        """检查权限"""
        return permission in self.get_user_permissions(role)


# 全局实例
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """获取认证服务"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


# ==================== FastAPI依赖 ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> TokenData:
    """获取当前用户"""
    auth_service = get_auth_service()
    
    token = credentials.credentials
    token_data = auth_service.verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_data


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """获取当前活跃用户"""
    # 这里可以添加额外检查，如用户是否被禁用
    return current_user


def require_role(allowed_roles: List[str]):
    """角色检查装饰器"""
    def role_checker(user: TokenData = Depends(get_current_active_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"需要角色: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker


def require_permission(permission: Permission):
    """权限检查装饰器"""
    def permission_checker(user: TokenData = Depends(get_current_active_user)):
        auth_service = get_auth_service()
        if not auth_service.has_permission(user.role, permission):
            raise HTTPException(
                status_code=403,
                detail=f"需要权限: {permission.value}"
            )
        return user
    return permission_checker


# ==================== API路由 ====================

from fastapi import APIRouter, HTTPException
from fastapi import Depends as FastAPIDepends

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """用户登录"""
    auth_service = get_auth_service()
    
    user = auth_service.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )
    
    access_token = auth_service.create_access_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate):
    """用户注册"""
    # 简化实现：直接返回创建的用户
    # 实际需要保存到数据库
    return {
        "id": str(uuid.uuid4()),
        "username": user_create.username,
        "email": user_create.email,
        "full_name": user_create.full_name,
        "role": user_create.role,
        "is_active": True
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: TokenData = FastAPIDepends(get_current_active_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "email": f"{current_user.username}@aisecops.local",
        "full_name": current_user.username,
        "role": current_user.role,
        "is_active": True
    }


@router.get("/permissions")
async def get_permissions(current_user: TokenData = FastAPIDepends(get_current_active_user)):
    """获取当前用户权限"""
    auth_service = get_auth_service()
    permissions = auth_service.get_user_permissions(current_user.role)
    
    return {
        "role": current_user.role,
        "permissions": [p.value for p in permissions]
    }


@router.get("/users")
async def list_users(
    current_user: TokenData = FastAPIDepends(
        require_permission(Permission.USER_VIEW)
    )
):
    """列出用户"""
    # 简化实现
    return {
        "users": [
            {"id": "user-001", "username": "admin", "role": "admin", "is_active": True},
            {"id": "user-002", "username": "analyst", "role": "analyst", "is_active": True},
            {"id": "user-003", "username": "viewer", "role": "viewer", "is_active": True}
        ]
    }


# ==================== 中间件 ====================

class RBACMiddleware:
    """RBAC中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # 这里可以添加请求级别的权限检查
        await self.app(scope, receive, send)
