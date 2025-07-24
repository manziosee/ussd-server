from fastapi import FastAPI, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from app.ussd_engine import USSDSessionManager
from app.config import settings
import uuid
import logging
from typing import Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    debug=settings.DEBUG,
    title="USSD Server",
    description="A robust USSD service implementation",
    version="1.0.0"
)

ussd_manager = USSDSessionManager()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    """Verify API key for protected endpoints"""
    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="API key authentication not configured"
        )
        
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    return api_key

@app.post("/ussd")
async def handle_ussd(
    session_id: str = Form(default_factory=lambda: str(uuid.uuid4())),
    phone_number: str = Form(...),
    user_input: str = Form(""),
    network_code: Optional[str] = Form(None),
    service_code: Optional[str] = Form(None)
):
    """
    Handle USSD requests
    
    Args:
        session_id: Unique session identifier
        phone_number: User's phone number
        user_input: User's input
        network_code: Mobile network code
        service_code: USSD service code
    """
    try:
        logger.info(
            f"USSD request - Session: {session_id}, "
            f"Phone: {phone_number}, "
            f"Input: '{user_input}'"
        )
        
        if not phone_number:
            raise ValueError("Phone number is required")
            
        response = ussd_manager.handle_request(
            session_id=session_id,
            user_input=user_input.strip(),
            phone_number=phone_number,
            network_code=network_code,
            service_code=service_code
        )
        
        logger.info(f"USSD response for {phone_number}: {response}")
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error handling USSD request: {str(e)}", exc_info=True)
        return {"response": f"END System error occurred. Please try again later."}

@app.get("/sessions/active")
async def get_active_sessions(_: str = Depends(verify_api_key)):
    """Get all active sessions (requires API key)"""
    try:
        active_sessions = ussd_manager.get_active_sessions()
        return JSONResponse(
            content={"sessions": active_sessions},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error fetching active sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve active sessions"
        )

@app.get("/sessions/cleanup")
async def cleanup_sessions(_: str = Depends(verify_api_key)):
    """Cleanup expired sessions (requires API key)"""
    try:
        count = ussd_manager.cleanup_sessions()
        return JSONResponse(
            content={"message": f"Cleaned up {count} expired sessions"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not cleanup sessions"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )