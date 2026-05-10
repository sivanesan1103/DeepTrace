import os
import time
import uuid
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize FastAPI app
app = FastAPI(
    title="API Gateway Service",
    description="Gateway service with routing, auth middleware, and rate limiting",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "proxy", "description": "Proxy endpoints to backend services"},
        {"name": "metrics", "description": "Prometheus metrics endpoints"},
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for rate limiting
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {e}")
    redis_client = None

# Prometheus metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total requests processed',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'gateway_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# Service routing map
SERVICE_ROUTES = {
    "/auth": "http://auth-service:8000",
    "/search": "http://search-service:8000",
    # Add more service routes as needed
}

# HTTP client for proxying
http_client = httpx.AsyncClient(timeout=30.0)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Generate and propagate request ID"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log requests and responses"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate latency
    process_time = time.time() - start_time
    
    # Log request/response
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'} "
        f"-> {response.status_code} ({process_time:.3f}s)"
    )
    
    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiter using Redis token bucket algorithm"""
    if not redis_client:
        # If Redis is not available, skip rate limiting
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limit settings (requests per minute)
    limit = 60
    window = 60  # seconds
    
    try:
        key = f"rate_limit:{client_ip}"
        current = redis_client.get(key)
        
        if current is None:
            # First request, set expiration
            redis_client.setex(key, window, 1)
        else:
            current = int(current)
            if current >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            redis_client.incr(key)
    except Exception as e:
        logger.warning(f"Rate limiting error: {e}")
        # Continue without rate limiting on error
    
    return await call_next(request)


@app.middleware("http")
async def jwt_validation_middleware(request: Request, call_next):
    """JWT validation middleware"""
    # Skip validation for health, metrics, docs endpoints
    if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Extract token from Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        # For non-protected routes, continue (services can handle their own auth)
        return await call_next(request)
    
    token = authorization.split(" ")[1]
    
    try:
        # Call auth-service to verify token
        response = await http_client.post(
            f"{AUTH_SERVICE_URL}/auth/verify",
            json={"token": token},
            timeout=5.0
        )
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )
        
        # Optionally add user info to request state
        user_data = response.json()
        request.state.user = user_data.get("user")
        
    except Exception as e:
        logger.warning(f"JWT validation error: {e}")
        # Continue without validation on error (fail open for robustness)
        pass
    
    return await call_next(request)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gateway-service",
        "timestamp": time.time()
    }


@app.get("/metrics", tags=["metrics"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI"""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"], tags=["proxy"])
async def proxy(request: Request, full_path: str):
    """Catch-all proxy to backend services"""
    # Determine target service based on path prefix
    target_service = None
    for prefix, service_url in SERVICE_ROUTES.items():
        if full_path.startswith(prefix.lstrip("/")):
            target_service = service_url
            # Remove the prefix from the path for forwarding
            forwarded_path = full_path[len(prefix.lstrip("/")):]
            break
    
    if not target_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Construct target URL
    target_url = f"{target_service}/{forwarded_path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
    
    # Prepare headers (exclude hop-by-hop headers)
    headers = dict(request.headers)
    headers_to_remove = ["host", "content-length"]
    for header in headers_to_remove:
        headers.pop(header, None)
    
    # Add request ID header
    headers["X-Request-ID"] = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Get request body
    body = await request.body()
    
    try:
        # Forward request to target service
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            timeout=30.0
        )
        
        # Prepare response headers (exclude hop-by-hop headers)
        response_headers = dict(response.headers)
        headers_to_remove = ["content-length", "transfer-encoding", "connection"]
        for header in headers_to_remove:
            response_headers.pop(header, None)
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type")
        )
    except httpx.RequestError as e:
        logger.error(f"Proxy request error: {e}")
        raise HTTPException(status_code=502, detail="Bad gateway")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Gateway service starting up")
    # Test Redis connection
    if redis_client:
        try:
            redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis on startup: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Gateway service shutting down")
    await http_client.aclose()
    if redis_client:
        redis_client.close()