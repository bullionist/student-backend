from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time
import sys
import os

from app.config import settings
from app.routers import program, student, admin

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="{time} {level} {message}",
    level="INFO" if settings.APP_ENV == "production" else "DEBUG"
)
logger.add(
    "logs/api.log",
    rotation="10 MB",
    retention="1 week",
    level="INFO"
)

app = FastAPI(
    title="AI-Powered Student Counseling Platform API",
    description="Backend API for the AI-Powered Student Counseling Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get request details
    method = request.method
    url = request.url.path
    
    # Log the request
    logger.info(f"Request started: {method} {url}")
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log the response
        logger.info(f"Request completed: {method} {url} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {method} {url} - Error: {str(e)} - Time: {process_time:.3f}s")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include routers
app.include_router(program.router)
app.include_router(student.router)
app.include_router(admin.router)

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint to check if the API is running."""
    return {
        "message": "Welcome to the AI-Powered Student Counseling Platform API",
        "docs": "/docs",
        "environment": settings.APP_ENV
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the API is running correctly."""
    return {
        "status": "ok",
        "api_version": "1.0.0",
        "environment": settings.APP_ENV
    }

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_ENV != "production"
    )
