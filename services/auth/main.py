import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import redis
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

from routers import token, verify, users, roles

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")

# Keycloak admin token cache
admin_token_cache = {"token": None, "expires_at": 0}

# Redis client
redis_client = redis.from_url(REDIS_URL)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app
app = FastAPI(title="Auth Service", version="0.1.0")

# Security
security = HTTPBearer()

# Include routers
app.include_router(token.router, prefix="/auth/token", tags=["token"])
app.include_router(verify.router, prefix="/auth/verify", tags=["verify"])
app.include_router(users.router, prefix="/auth/users", tags=["users"])
app.include_router(roles.router, prefix="/auth/roles", tags=["roles"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting auth service...")
    # Validate Keycloak realm
    await validate_keycloak_realm()
    logger.info("Auth service started successfully")

async def validate_keycloak_realm():
    """Validate that the Keycloak realm is accessible"""
    try:
        async with httpx.AsyncClient() as client:
            # Get admin token
            token_url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET
            }
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()
            token_info = response.json()
            
            # Cache admin token
            admin_token_cache["token"] = token_info["access_token"]
            # Calculate expiration (subtract 60 seconds for safety)
            admin_token_cache["expires_at"] = token_info["expires_in"] + token_info.get("issued_at", 0) - 60
            
            # Check realm info
            realm_url = f"{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}"
            headers = {"Authorization": f"Bearer {admin_token_cache['token']}"}
            realm_response = await client.get(realm_url, headers=headers)
            realm_response.raise_for_status()
            logger.info(f"Connected to Keycloak realm: {KEYCLOAK_REALM}")
    except Exception as e:
        logger.error(f"Failed to connect to Keycloak: {e}")
        raise

# Dependency to get admin token
async def get_admin_token():
    """Get valid admin token, refreshing if necessary"""
    import time
    current_time = time.time()
    if admin_token_cache["token"] is None or current_time >= admin_token_cache["expires_at"]:
        await validate_keycloak_realm()
    return admin_token_cache["token"]

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify token via Keycloak introspection endpoint"""
    token = credentials.credentials
    try:
        async with httpx.AsyncClient() as client:
            introspection_url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
            data = {
                "token": token,
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET
            }
            response = await client.post(introspection_url, data=data)
            response.raise_for_status()
            token_info = response.json()
            
            if not token_info.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token_info
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to check admin role
async def require_admin_user(current_user: dict = Depends(get_current_user)):
    """Require admin role for endpoint access"""
    # Check if user has admin role (realm-level or client-level)
    # This is a simplified check - in practice you might check specific roles
    realm_roles = current_user.get("realm_access", {}).get("roles", [])
    resource_access = current_user.get("resource_access", {})
    client_roles = []
    for client_access in resource_access.values():
        client_roles.extend(client_access.get("roles", []))
    
    all_roles = set(realm_roles + client_roles)
    if "admin" not in all_roles and "manage-users" not in all_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user

# Make dependencies available to routers
app.dependency_overrides[get_admin_token] = get_admin_token
app.dependency_overrides[get_db] = get_db
app.dependency_overrides[get_current_user] = get_current_user
app.dependency_overrides[require_admin_user] = require_admin_user