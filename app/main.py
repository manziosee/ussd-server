from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from app.ussd_engine import USSDSessionManager
import uuid
from app.config import settings

app = FastAPI(debug=settings.DEBUG)
ussd_manager = USSDSessionManager()

@app.post("/ussd")
async def handle_ussd(
    session_id: str = Form(default_factory=lambda: str(uuid.uuid4())),
    phone_number: str = Form(None),
    user_input: str = Form("")
):
    try:
        response = ussd_manager.handle_request(
            session_id=session_id,
            user_input=user_input.strip(),
            phone_number=phone_number
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sessions")
async def get_active_sessions():
    return JSONResponse(ussd_manager.sessions)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)