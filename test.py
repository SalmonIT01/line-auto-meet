from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
from datetime import datetime
import requests
import aiosmtplib
from email.message import EmailMessage
import os
import time

app = FastAPI()


class Creator(BaseModel):
    email: str
    self: bool


class Event(BaseModel):
    id: str
    summary: str
    start: str
    end: str
    creator: Creator
    attendees: List[Any]
    status: str
    location: str = ""
    description: str = ""


class CalendarResult(BaseModel):
    email: str
    calendar_id: str
    events: List[Event]
    is_authenticated: bool


class CalendarInput(BaseModel):
    results: List[CalendarResult]


@app.post("/calendar/parse")
async def parse_calendar(data: CalendarInput):
    calendar_data = {}

    for result in data.results:
        email = result.email
        if email not in calendar_data:
            calendar_data[email] = {}

        for event in result.events:
            start = event.start
            end = event.end

            if 'T' not in start:
                date = start
                time_start = "00:00"
                time_end = "23:59"
            else:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                date = start_dt.date().isoformat()
                time_start = start_dt.strftime("%H:%M")
                time_end = end_dt.strftime("%H:%M")

            if date not in calendar_data[email]:
                calendar_data[email][date] = []

            calendar_data[email][date].append((time_start, time_end))

    return calendar_data

def send_post(meeting_result):
    start = time.time()
    try:
        response = requests.post(
            "http://127.0.0.1:8000/getmeeting",
            json=meeting_result.dict(),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print("✅ POST สำเร็จ:", response.status_code)
    except Exception as e:
        print("❌ POST ล้มเหลว:", str(e))
        
    finally:
        print(f"⏱️ ใช้เวลา: {round(time.time() - start, 2)} วินาที")

def send_get(email):
    start = time.time()
    try:
        response = requests.get(
            f"http://127.0.0.1:8000/events/{email}",
            timeout=15
        )
        print(f"✅ GET สำเร็จ: {response.status_code}")
        print(f"📡 URL: http://127.0.0.1:8000/events/{email}")
        return response.json()
    except Exception as e:
        print(f"❌ GET ล้มเหลว: {str(e)}")
        return {"error": str(e)}
    finally:
        print(f"⏱️ ใช้เวลา: {round(time.time() - start, 2)} วินาที")

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = os.getenv("email")
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username= os.getenv("email"),
        password= os.getenv("password")  # ใช้ App Password ถ้าใช้ Gmail
    )