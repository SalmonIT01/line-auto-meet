from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot.exceptions import InvalidSignatureError
from lineChatbot import *
import aiosmtplib
from email.message import EmailMessage
from test import send_email, send_post




app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    # Get X-Line-Signature header and request body
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_decode = body.decode("utf-8")
    
    try:
        # Handle webhook body
        handler.handle(body_decode, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return JSONResponse(content={"status": "OK"})
    
@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "LINE Bot Meeting Scheduler is running"}

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "LINE Bot Meeting Scheduler is running"}

@app.get("/meetings/{user_id}")
def get_user_meetings(user_id: str):
    """Get user meetings (mock endpoint for demonstration)"""
    # In production, fetch from database
    return {"user_id": user_id, "meetings": []}


@app.post("/getmeeting")
async def receive_meeting(request: Request):
    data = await request.json()
    print("📥 ได้รับข้อมูลจาก LINE BOT:", data)

    subject = f"นัดปลาชุมกันนน [ชื่อ : {data['summary']}]"
    body = f"""📝 ข้อมูลการประชุม:

📌 ชื่อ: {data['summary']}
📆 วันที่: {data['start_time'].split('T')[0]}
🕒 เวลา: {data['start_time'].split('T')[1][:5]} - {data['end_time'].split('T')[1][:5]}

👥 ผู้เข้าร่วม:
""" + "\n".join(f"- {email}" for email in data["user_emails"])

    for email in data["user_emails"]:
        await send_email(email, subject, body)

    return JSONResponse(content={"status": "received", "detail": "ได้รับข้อมูลและส่งอีเมลแล้ว"})



@app.get("/{email}")
async def login(email: str, request: Request):
    print('kuy')
    return {"message": "เข้าสู่ระบบสำเร็จ! คุณสามารถกลับไปใช้งาน LINE Bot ได้แล้ว"}

if __name__ == "__main__":
    import uvicorn
    # For local development
    uvicorn.run(app, host="localhost", port=8000)