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
    "gemini_api_key": None,
    "chat_history": []  # Store conversation history for better memory
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
        return json.dumps({"error": "Not authenticated"})
    
    try:
        mail.select("inbox")
        
        # Search for emails
        search_crit = "ALL"
        if query and query != "ALL":
            search_crit = f'(SUBJECT "{query}")'
            
        status, search_data = mail.search(None, search_crit)
        if status != 'OK' or not search_data[0]:
            # Fallback to ALL if search fails
            _, search_data = mail.search(None, "ALL")

        mail_ids = search_data[0].split()
        if not mail_ids:
            mail.close()
            mail.logout()
            return json.dumps([])
        
        # Get latest emails
        latest_ids = mail_ids[-int(limit):]
        latest_ids.reverse()
        
        emails_data = []
        for i in latest_ids:
            try:
                _, msg_data = mail.fetch(i, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Get subject safely
                        subject = "No Subject"
                        if msg.get("Subject"):
                            try:
                                decoded_parts = decode_header(msg["Subject"])
                                subject_parts = []
                                for content, encoding in decoded_parts:
                                    if isinstance(content, bytes):
                                        subject_parts.append(content.decode(encoding if encoding else "utf-8", errors="ignore"))
                                    else:
                                        subject_parts.append(str(content))
                                subject = "".join(subject_parts)
                            except:
                                subject = str(msg.get("Subject", "No Subject"))
                        
                        # Get sender safely
                        sender = msg.get("From", "Unknown Sender")
                        
                        # Get body safely
                        body = ""
                        try:
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            payload = part.get_payload(decode=True)
                                            if payload:
                                                body = payload.decode("utf-8", errors="ignore")
                                                break
                                        except:
                                            continue
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    body = payload.decode("utf-8", errors="ignore")
                        except:
                            body = "Could not decode email body"
                        
                        emails_data.append({
                            "id": str(int(i)),
                            "sender": sender,
                            "subject": subject,
                            "body_snippet": body[:200] if body else "No content"
                        })
            except Exception as e:
                print(f"Error processing email {i}: {str(e)}")
                continue
        
        mail.close()
        mail.logout()
        return json.dumps(emails_data)
    except Exception as e:
        print(f"Error in fetch_emails_tool: {str(e)}")
        return json.dumps({"error": f"Error fetching emails: {str(e)}"})

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

def delete_email_tool(email_id):
    """Deletes an email by ID."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    try:
        mail.select("inbox")
        mail.store(email_id, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.close()
        mail.logout()
        return f"Email {email_id} deleted successfully"
    except Exception as e:
        return f"Error deleting email: {str(e)}"

def mark_as_read_tool(email_id):
    """Marks an email as read."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    try:
        mail.select("inbox")
        mail.store(email_id, '+FLAGS', '\\Seen')
        mail.close()
        mail.logout()
        return f"Email {email_id} marked as read"
    except Exception as e:
        return f"Error marking as read: {str(e)}"

def mark_as_unread_tool(email_id):
    """Marks an email as unread."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    try:
        mail.select("inbox")
        mail.store(email_id, '-FLAGS', '\\Seen')
        mail.close()
        mail.logout()
        return f"Email {email_id} marked as unread"
    except Exception as e:
        return f"Error marking as unread: {str(e)}"

def search_emails_tool(sender=None, subject=None, date_from=None, date_to=None):
    """Advanced email search by sender, subject, or date range."""
    mail = get_imap_connection()
    if not mail:
        return json.dumps({"error": "Not authenticated"})
    
    try:
        mail.select("inbox")
        
        # Build search criteria
        search_parts = []
        if sender:
            search_parts.append(f'FROM "{sender}"')
        if subject:
            search_parts.append(f'SUBJECT "{subject}"')
        if date_from:
            search_parts.append(f'SINCE "{date_from}"')
        if date_to:
            search_parts.append(f'BEFORE "{date_to}"')
        
        search_crit = ' '.join(search_parts) if search_parts else "ALL"
        
        _, search_data = mail.search(None, search_crit)
        mail_ids = search_data[0].split()
        
        if not mail_ids:
            mail.close()
            mail.logout()
            return json.dumps([])
        
        # Get latest 10 matching emails
        latest_ids = mail_ids[-10:]
        latest_ids.reverse()
        
        emails_data = []
        for i in latest_ids:
            try:
                _, msg_data = mail.fetch(i, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject_text = "No Subject"
                        if msg.get("Subject"):
                            try:
                                decoded_parts = decode_header(msg["Subject"])
                                subject_parts = []
                                for content, encoding in decoded_parts:
                                    if isinstance(content, bytes):
                                        subject_parts.append(content.decode(encoding if encoding else "utf-8", errors="ignore"))
                                    else:
                                        subject_parts.append(str(content))
                                subject_text = "".join(subject_parts)
                            except:
                                subject_text = str(msg.get("Subject", "No Subject"))
                        
                        emails_data.append({
                            "id": str(int(i)),
                            "sender": msg.get("From", "Unknown"),
                            "subject": subject_text,
                            "date": msg.get("Date", "Unknown")
                        })
            except:
                continue
        
        mail.close()
        mail.logout()
        return json.dumps(emails_data)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})

def get_email_details_tool(email_id):
    """Gets full email details including body and attachments info."""
    mail = get_imap_connection()
    if not mail:
        return json.dumps({"error": "Not authenticated"})
    
    try:
        mail.select("inbox")
        _, msg_data = mail.fetch(str(email_id), "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Get subject
                subject = "No Subject"
                if msg.get("Subject"):
                    try:
                        decoded_parts = decode_header(msg["Subject"])
                        subject_parts = []
                        for content, encoding in decoded_parts:
                            if isinstance(content, bytes):
                                subject_parts.append(content.decode(encoding if encoding else "utf-8", errors="ignore"))
                            else:
                                subject_parts.append(str(content))
                        subject = "".join(subject_parts)
                    except:
                        subject = str(msg.get("Subject", "No Subject"))
                
                # Get body
                body = ""
                attachments = []
                
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                attachments.append(filename)
                        elif content_type == "text/plain" and not body:
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode("utf-8", errors="ignore")
                            except:
                                pass
                else:
                    try:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                    except:
                        body = "Could not decode"
                
                mail.close()
                mail.logout()
                
                return json.dumps({
                    "id": email_id,
                    "from": msg.get("From", "Unknown"),
                    "to": msg.get("To", "Unknown"),
                    "subject": subject,
                    "date": msg.get("Date", "Unknown"),
                    "body": body[:1000],  # Limit to 1000 chars
                    "attachments": attachments
                })
        
        mail.close()
        mail.logout()
        return json.dumps({"error": "Email not found"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

def reply_to_email_tool(email_id, reply_body):
    """Replies to an email."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        # Get original email
        mail.select("inbox")
        _, msg_data = mail.fetch(str(email_id), "(RFC822)")
        
        original_msg = None
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                original_msg = email.message_from_bytes(response_part[1])
                break
        
        if not original_msg:
            return "Error: Original email not found"
        
        # Get original sender and subject
        to_email = original_msg.get("From")
        original_subject = original_msg.get("Subject", "")
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
        
        mail.close()
        mail.logout()
        
        # Send reply
        server = get_smtp_connection()
        if not server:
            return "Error: SMTP connection failed"
        
        msg = MIMEMultipart()
        msg['From'] = active_session["email"]
        msg['To'] = to_email
        msg['Subject'] = reply_subject
        msg['In-Reply-To'] = original_msg.get("Message-ID", "")
        msg['References'] = original_msg.get("Message-ID", "")
        msg.attach(MIMEText(reply_body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        return f"Reply sent successfully to {to_email}"
    except Exception as e:
        return f"Error replying: {str(e)}"

def forward_email_tool(email_id, to_email, message=""):
    """Forwards an email to another recipient."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        mail.select("inbox")
        _, msg_data = mail.fetch(str(email_id), "(RFC822)")
        
        original_msg = None
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                original_msg = email.message_from_bytes(response_part[1])
                break
        
        if not original_msg:
            return "Error: Original email not found"
        
        original_subject = original_msg.get("Subject", "")
        forward_subject = f"Fwd: {original_subject}" if not original_subject.startswith("Fwd:") else original_subject
        
        # Get original body
        original_body = ""
        if original_msg.is_multipart():
            for part in original_msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            original_body = payload.decode("utf-8", errors="ignore")
                            break
                    except:
                        pass
        else:
            try:
                payload = original_msg.get_payload(decode=True)
                if payload:
                    original_body = payload.decode("utf-8", errors="ignore")
            except:
                pass
        
        mail.close()
        mail.logout()
        
        # Send forward
        server = get_smtp_connection()
        if not server:
            return "Error: SMTP connection failed"
        
        msg = MIMEMultipart()
        msg['From'] = active_session["email"]
        msg['To'] = to_email
        msg['Subject'] = forward_subject
        
        forward_body = f"{message}\n\n---------- Forwarded message ----------\n{original_body}"
        msg.attach(MIMEText(forward_body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        return f"Email forwarded successfully to {to_email}"
    except Exception as e:
        return f"Error forwarding: {str(e)}"

def create_draft_tool(to_email, subject, body):
    """Creates a draft email (saves to Drafts folder)."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = active_session["email"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Save to Drafts
        mail.select("[Gmail]/Drafts")
        mail.append("[Gmail]/Drafts", '', imaplib.Time2Internaldate(None), msg.as_bytes())
        
        mail.close()
        mail.logout()
        
        return f"Draft created successfully for {to_email}"
    except Exception as e:
        return f"Error creating draft: {str(e)}"

def archive_email_tool(email_id):
    """Archives an email (removes from inbox, keeps in All Mail)."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        mail.select("inbox")
        # Move to All Mail by removing Inbox label
        mail.store(email_id, '-X-GM-LABELS', '\\Inbox')
        mail.close()
        mail.logout()
        return f"Email {email_id} archived successfully"
    except Exception as e:
        # Fallback: just remove from inbox
        try:
            mail.select("inbox")
            mail.store(email_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            mail.close()
            mail.logout()
            return f"Email {email_id} removed from inbox"
        except:
            return f"Error archiving: {str(e)}"

def star_email_tool(email_id):
    """Stars/flags an email."""
    mail = get_imap_connection()
    if not mail:
        return "Error: Not authenticated."
    
    try:
        mail.select("inbox")
        mail.store(email_id, '+FLAGS', '\\Flagged')
        mail.close()
        mail.logout()
        return f"Email {email_id} starred successfully"
    except Exception as e:
        return f"Error starring email: {str(e)}"

def extract_contacts_tool(limit=20):
    """Extracts unique email contacts from recent emails."""
    mail = get_imap_connection()
    if not mail:
        return json.dumps({"error": "Not authenticated"})
    
    try:
        mail.select("inbox")
        _, search_data = mail.search(None, "ALL")
        mail_ids = search_data[0].split()
        
        if not mail_ids:
            mail.close()
            mail.logout()
            return json.dumps([])
        
        latest_ids = mail_ids[-int(limit):]
        contacts = set()
        
        for i in latest_ids:
            try:
                _, msg_data = mail.fetch(i, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        sender = msg.get("From", "")
                        if sender and "@" in sender:
                            # Extract email from "Name <email@domain.com>" format
                            import re
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+', sender)
                            if email_match:
                                contacts.add(email_match.group(0))
            except:
                continue
        
        mail.close()
        mail.logout()
        
        return json.dumps(list(contacts)[:50])  # Return max 50 unique contacts
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

def schedule_email_tool(to_email, subject, body, send_time):
    """Schedules an email to be sent later (creates draft with note)."""
    # Note: Gmail doesn't support native scheduling via IMAP
    # This creates a draft with scheduling info in the body
    
    scheduled_body = f"[SCHEDULED FOR: {send_time}]\n\n{body}\n\n---\nNote: This is a draft. Please use Gmail's schedule send feature to set the actual send time."
    
    return create_draft_tool(to_email, subject, scheduled_body)

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
    active_session.update({
        "email": None, 
        "password": None, 
        "authenticated": False, 
        "gemini_api_key": None,
        "chat_history": []
    })
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

@app.post("/api/clear-history")
def clear_chat_history():
    """Clear chat history to start fresh conversation"""
    active_session["chat_history"] = []
    return {"status": "success", "message": "Chat history cleared"}

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
    # Role & Objective
You are an Elite AI Email Concierge. Your purpose is to manage the user's Gmail inbox with high efficiency, precision, and privacy. You act as an intelligent bridge between the user and their email data.

# Tool Capabilities & Logic
You have access to 15 specific tools. Use them intelligently based on the user's intent:

## A. Retrieval (Finding Info)
- Use `fetch_emails(limit, query)` for general browsing or "checking latest emails."
- Use `search_emails(...)` when specific filters (Sender, Date, Subject) are provided.
- Use `get_email_details(email_id)` ONLY when the user asks to read a specific email's full content or needs to summarize a long thread.
- Use `count_unread()` for status updates.
- Use `extract_contacts(limit)` for relationship management.

## B. Action (Communication)
- `send_email`: Write professional, concise emails. Always maintain the user's voice.
- `reply_to_email` & `forward_email`: Always reference context from the original thread.
- `create_draft`: Use this when the request is ambiguous or requires user review before sending.
- `schedule_email`: Use when timing is specified (e.g., "send this tomorrow morning").

## C. Organization (Inbox Zero)
- `archive_email`, `delete_email`: Use carefully. 
- `mark_as_read`, `mark_as_unread`, `star_email`: Use to prioritize important items.

# Operational Guidelines (CRITICAL)
1. **Think Before Acting:** Analyze the request. If the user says "Find that invoice from Google," prefer `search_emails` over `fetch_emails`.
2. **Chain of Actions:** You can chain tools. Example: Search for an email -> Get its ID -> Reply to it.
3. **Safety First:** If a request involves deleting multiple emails or sending sensitive info, ask for confirmation or create a draft first.
4. **Formatting:** Present output in clean Markdown. Use bullet points for email lists.
   - Format: **[Sender Name]**: *Subject Line* (Date/Time)
5. **Context Awareness:** Remember previous interactions in this session to handle follow-up questions like "Reply to that last email."

# Tone & Style
- Be helpful, direct, and professional.
- Do not make up information. If a tool returns no results, state clearly: "I couldn't find any emails matching that criteria."
    """
    
    try:
        model_name = req.model if req.model else "gemini-2.5-flash"
        
        # Define all 15 tools
        tools = [
            {
                "function_declarations": [
                    {
                        "name": "fetch_emails",
                        "description": "Fetches emails from the inbox. Returns a JSON list of recent emails with sender, subject, and body snippet.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "limit": {
                                    "type_": "INTEGER",
                                    "description": "Number of emails to fetch (default: 10)"
                                },
                                "query": {
                                    "type_": "STRING",
                                    "description": "Search query - can be a subject keyword or 'ALL' for all emails"
                                }
                            }
                        }
                    },
                    {
                        "name": "send_email",
                        "description": "Sends an email to a specified recipient.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "to_email": {
                                    "type_": "STRING",
                                    "description": "Recipient email address"
                                },
                                "subject": {
                                    "type_": "STRING",
                                    "description": "Email subject line"
                                },
                                "body": {
                                    "type_": "STRING",
                                    "description": "Email body content"
                                }
                            },
                            "required": ["to_email", "subject", "body"]
                        }
                    },
                    {
                        "name": "count_unread",
                        "description": "Counts the number of unread emails in the inbox.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {}
                        }
                    },
                    {
                        "name": "delete_email",
                        "description": "Deletes an email by its ID.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to delete"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "mark_as_read",
                        "description": "Marks an email as read.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to mark as read"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "mark_as_unread",
                        "description": "Marks an email as unread.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to mark as unread"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "search_emails",
                        "description": "Advanced email search by sender, subject, or date range. Returns matching emails.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "sender": {
                                    "type_": "STRING",
                                    "description": "Filter by sender email address"
                                },
                                "subject": {
                                    "type_": "STRING",
                                    "description": "Filter by subject keywords"
                                },
                                "date_from": {
                                    "type_": "STRING",
                                    "description": "Start date in format DD-Mon-YYYY (e.g., 01-Jan-2024)"
                                },
                                "date_to": {
                                    "type_": "STRING",
                                    "description": "End date in format DD-Mon-YYYY"
                                }
                            }
                        }
                    },
                    {
                        "name": "get_email_details",
                        "description": "Gets full email details including complete body and attachment information.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to get details for"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "reply_to_email",
                        "description": "Replies to an email. Automatically includes Re: in subject and proper threading.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to reply to"
                                },
                                "reply_body": {
                                    "type_": "STRING",
                                    "description": "The reply message content"
                                }
                            },
                            "required": ["email_id", "reply_body"]
                        }
                    },
                    {
                        "name": "forward_email",
                        "description": "Forwards an email to another recipient with optional message.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to forward"
                                },
                                "to_email": {
                                    "type_": "STRING",
                                    "description": "Recipient email address"
                                },
                                "message": {
                                    "type_": "STRING",
                                    "description": "Optional message to add before forwarded content"
                                }
                            },
                            "required": ["email_id", "to_email"]
                        }
                    },
                    {
                        "name": "create_draft",
                        "description": "Creates a draft email and saves it to the Drafts folder.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "to_email": {
                                    "type_": "STRING",
                                    "description": "Recipient email address"
                                },
                                "subject": {
                                    "type_": "STRING",
                                    "description": "Email subject"
                                },
                                "body": {
                                    "type_": "STRING",
                                    "description": "Email body content"
                                }
                            },
                            "required": ["to_email", "subject", "body"]
                        }
                    },
                    {
                        "name": "archive_email",
                        "description": "Archives an email (removes from inbox but keeps in All Mail).",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to archive"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "star_email",
                        "description": "Stars/flags an email for importance.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "email_id": {
                                    "type_": "STRING",
                                    "description": "The ID of the email to star"
                                }
                            },
                            "required": ["email_id"]
                        }
                    },
                    {
                        "name": "extract_contacts",
                        "description": "Extracts unique email contacts from recent emails.",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "limit": {
                                    "type_": "INTEGER",
                                    "description": "Number of recent emails to scan (default: 20)"
                                }
                            }
                        }
                    },
                    {
                        "name": "schedule_email",
                        "description": "Schedules an email to be sent later (creates draft with scheduling note).",
                        "parameters": {
                            "type_": "OBJECT",
                            "properties": {
                                "to_email": {
                                    "type_": "STRING",
                                    "description": "Recipient email address"
                                },
                                "subject": {
                                    "type_": "STRING",
                                    "description": "Email subject"
                                },
                                "body": {
                                    "type_": "STRING",
                                    "description": "Email body content"
                                },
                                "send_time": {
                                    "type_": "STRING",
                                    "description": "When to send (e.g., 'tomorrow 9am', 'Dec 10 2pm')"
                                }
                            },
                            "required": ["to_email", "subject", "body", "send_time"]
                        }
                    }
                ]
            }
        ]
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            tools=tools
        )
        
        # Build conversation history manually for powerful memory
        # Convert stored history to proper format
        conversation_history = []
        
        # Add previous messages from session (last 10 exchanges = 20 messages)
        if active_session["chat_history"]:
            for msg in active_session["chat_history"][-20:]:
                if msg.get("role") == "user":
                    conversation_history.append({
                        "role": "user",
                        "parts": [{"text": msg.get("content", "")}]
                    })
                elif msg.get("role") == "model":
                    conversation_history.append({
                        "role": "model", 
                        "parts": [{"text": msg.get("content", "")}]
                    })
        
        # Start chat with history
        chat = model.start_chat(history=conversation_history)
        
        # Function mapping for all 15 tools
        function_map = {
            "fetch_emails": fetch_emails_tool,
            "send_email": send_email_tool,
            "count_unread": count_unread_tool,
            "delete_email": delete_email_tool,
            "mark_as_read": mark_as_read_tool,
            "mark_as_unread": mark_as_unread_tool,
            "search_emails": search_emails_tool,
            "get_email_details": get_email_details_tool,
            "reply_to_email": reply_to_email_tool,
            "forward_email": forward_email_tool,
            "create_draft": create_draft_tool,
            "archive_email": archive_email_tool,
            "star_email": star_email_tool,
            "extract_contacts": extract_contacts_tool,
            "schedule_email": schedule_email_tool
        }
        
        # Send user message
        response = chat.send_message(req.command)
        
        # Handle function calls manually
        max_iterations = 5
        iteration = 0
        final_text = ""
        
        while iteration < max_iterations:
            iteration += 1
            
            # Validate response
            if not response or not response.candidates:
                final_text = "I apologize, but I couldn't generate a proper response. Please try again."
                break
            
            candidate = response.candidates[0]
            
            # Check if response has content
            if not candidate.content or not candidate.content.parts:
                final_text = "I received your message but couldn't generate a response. Please rephrase and try again."
                break
                
            part = candidate.content.parts[0]
            
            # Check if there's a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                function_name = function_call.name
                function_args = dict(function_call.args) if function_call.args else {}
                
                # Execute the function
                if function_name in function_map:
                    try:
                        result = function_map[function_name](**function_args)
                        
                        # Send the result back to the model
                        response = chat.send_message(
                            genai.protos.Content(
                                parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={"result": result}
                                    )
                                )]
                            )
                        )
                    except Exception as func_error:
                        # If function execution fails, send error back to model
                        try:
                            response = chat.send_message(
                                genai.protos.Content(
                                    parts=[genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response={"error": str(func_error)}
                                        )
                                    )]
                                )
                            )
                        except:
                            final_text = f"Error executing {function_name}: {str(func_error)}"
                            break
                else:
                    final_text = f"Unknown function: {function_name}"
                    break
            else:
                # No more function calls, we have the final response
                if hasattr(part, 'text') and part.text:
                    final_text = part.text
                else:
                    final_text = "I processed your request but couldn't generate a text response."
                break
        
        # Ensure we have a response
        if not final_text:
            if response and response.text:
                final_text = response.text
            else:
                final_text = "I apologize, but I couldn't complete your request. Please try again with a different question."
        
        # Save conversation to memory (user message + AI response)
        active_session["chat_history"].append({
            "role": "user",
            "content": req.command
        })
        active_session["chat_history"].append({
            "role": "model",
            "content": final_text
        })
        
        # Keep only last 30 messages (15 exchanges) for powerful memory
        if len(active_session["chat_history"]) > 30:
            active_session["chat_history"] = active_session["chat_history"][-30:]
        
        return {
            "type": "response",
            "message": final_text
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")  # Log to console
        return {
            "type": "error",
            "message": f"AI Error: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
