import os
import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

app = FastAPI(title="AI Email Assistant")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
active_session = {
    "email": None,
    "password": None,
    "authenticated": False,
    "gemini_api_key": None
}

class LoginRequest(BaseModel):
    email: str
    password: str



def get_imap_connection():
    if not active_session["authenticated"]:
        return None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(active_session["email"], active_session["password"])
        return mail
    except Exception as e:
        print(f"IMAP Connection Error: {e}")
        return None

def get_smtp_connection():
    if not active_session["authenticated"]:
        return None
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(active_session["email"], active_session["password"])
        return server
    except Exception as e:
        print(f"SMTP Connection Error: {e}")
        return None

# --- Email Tools ---

def fetch_emails_tool(limit=10, query="ALL"):
    """Fetches emails from the inbox."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        mail.select("inbox")
        # If query is simple text, try to search subject, otherwise ALL
        search_crit = "ALL"
        if query != "ALL":
            # Very basic search mapping
            search_crit = f'(SUBJECT "{query}")'
            
        status, search_data = mail.search(None, search_crit)
        if status != 'OK':
             # Fallback to ALL if search fails
             _, search_data = mail.search(None, "ALL")

        mail_ids = search_data[0].split()
        latest_ids = mail_ids[-limit:]
        latest_ids.reverse()
        
        emails_data = []
        for i in latest_ids:
            _, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    sender = msg.get("From")
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except: pass
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except: pass
                    
                    emails_data.append({
                        "id": str(int(i)),
                        "sender": sender,
                        "subject": subject,
                        "body_snippet": body[:200]
                    })
        mail.close()
        mail.logout()
        return json.dumps(emails_data)
    except Exception as e:
        return f"Error fetching emails: {str(e)}"

def send_email_tool(to_email, subject, body):
    """Sends an email."""
    server = get_smtp_connection()
    if not server:
        return "Error: Not authenticated."
    
    try:
        msg = MIMEMultipart()
        msg['From'] = active_session["email"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def count_unread_tool():
    """Counts unread emails."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    try:
        mail.select("inbox")
        _, search_data = mail.search(None, "UNSEEN")
        count = len(search_data[0].split())
        mail.close()
        mail.logout()
        return str(count)
    except Exception as e:
        return f"Error counting unread: {str(e)}"

# --- API Endpoints ---

@app.post("/auth/login")
def login(creds: LoginRequest):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(creds.email, creds.password)
        mail.logout()
        
        active_session["email"] = creds.email
        active_session["password"] = creds.password
        active_session["authenticated"] = True
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/logout")
def logout():
    active_session.update({"email": None, "password": None, "authenticated": False, "gemini_api_key": None})
    return {"status": "success"}

@app.get("/api/status")
def status():
    return {
        "authenticated": active_session["authenticated"], 
        "email": active_session["email"],
        "has_gemini_key": active_session["gemini_api_key"] is not None
    }

@app.post("/api/settings/gemini")
def set_gemini_key(key: str = Body(..., embed=True)):
    active_session["gemini_api_key"] = key
    return {"status": "success"}

@app.get("/api/emails")
def get_emails_endpoint():
    # Re-use the tool logic but return object
    res = fetch_emails_tool(limit=15)
    try:
        return {"emails": json.loads(res)}
    except:
        return {"emails": []}

class AgentRequest(BaseModel):
    command: str
    gemini_key: Optional[str] = None
    model: Optional[str] = "gemini-2.0-flash-exp"

@app.post("/api/agent")
async def agent_endpoint(req: AgentRequest):
    if not active_session["authenticated"]:
        raise HTTPException(status_code=401, detail="Please login first")
    
    api_key = req.gemini_key or active_session["gemini_api_key"]
    if not api_key:
        return {
            "type": "error", 
            "message": "Gemini API Key is missing. Please add it in settings."
        }
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # System Prompt
    system_instruction = """
    You are an advanced AI Email Assistant. You have access to the user's Gmail via tools.
    Your goal is to be helpful, efficient, and professional.
    
    Available Tools:
    1. fetch_emails(limit: int, query: str): Get recent emails. Query can be a subject keyword or 'ALL'.
    2. send_email(to_email: str, subject: str, body: str): Send an email.
    3. count_unread(): Get the number of unread emails.
    
    If the user asks to do something you have a tool for, use the tool.
    If the user asks a general question, answer it.
    If you use a tool, summarize the result for the user in a nice format.
    
    When listing emails, format them nicely with Markdown (bold subjects, etc).
    """
    
    try:
        model_name = req.model if req.model else "gemini-2.0-flash-exp"
        # Fallback if user selects something invalid, but frontend should handle list
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            tools=[fetch_emails_tool, send_email_tool, count_unread_tool]
        )
        
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(req.command)
        
        return {
            "type": "response",
            "message": response.text
        }
        
    except Exception as e:
        return {
            "type": "error",
            "message": f"AI Error ({model_name}): {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
