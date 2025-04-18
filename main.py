import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, QuickReply, QuickReplyButton, MessageAction,
    PostbackEvent, PostbackAction, DatetimePickerAction
)
from lineChatbot import *

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

# @app.post("/create-meeting")
# async def create_meeting(meeting: MeetingResult):
#     """Create a meeting (mock endpoint for demonstration)"""
#     # In production, save to database and integrate with calendar APIs
#     return {"status": "success", "meeting": meeting.dict()}

@app.post("/getmeeting")
async def receive_meeting(request: Request):
    data = await request.json()
    print("📥 ได้รับข้อมูลจาก LINE BOT:", data)
    return JSONResponse(content={"status": "received", "detail": "ได้รับข้อมูลเรียบร้อย"})


if __name__ == "__main__":
    import uvicorn
    # For local development
    uvicorn.run(app, host="localhost", port=8000)