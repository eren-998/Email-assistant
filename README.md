# 🤖 AI Gmail Agent - Professional Email Management

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/)

## 📋 Table of Contents
1. [Overview](#-overview)
2. [Features](#-features)
3. [Screenshots](#-screenshots)
4. [Installation](#-installation)
5. [Configuration](#%EF%B8%8F-configuration)
6. [Running the Application](#-running-the-application)
7. [Using the AI Agent](#-using-the-ai-agent)
8. [Available Tools](#%EF%B8%8F-available-tools)
9. [Troubleshooting](#-troubleshooting)
10. [Technical Details](#-technical-details)

---

## 🎯 Overview

**AI Gmail Agent** is a next-generation email management platform powered by Google's Gemini 2.5 Flash AI. It combines a sleek, modern Gmail-style interface with intelligent automation, providing **15 powerful tools** for comprehensive email operations through natural language commands.

### Key Highlights
- 🎨 **Modern Dark/Light Theme** - Professional Gmail-inspired UI
- 🤖 **15 AI-Powered Tools** - Complete email management suite
- 💬 **Natural Language Interface** - Chat with your inbox
- 🧠 **Conversation Memory** - Remembers context (30 messages)
- ⚡ **Real-time AI Summaries** - Auto-summarize emails on click
- 🔐 **Secure Gmail Integration** - IMAP/SMTP with App Passwords
- 🚀 **Lightning Fast** - React + Vite + FastAPI stack

---

## ✨ Features

### 🎨 Modern UI/UX
- **Gmail-Style Interface** - Familiar, intuitive design
- **Dark/Light Mode** - Eye-friendly themes
- **AI Chat Panel** - Always-visible assistant (450px wide)
- **Email Modal** - Full-screen email viewer with AI summary
- **Responsive Layout** - Adaptive sidebar and panels
- **Smooth Animations** - Framer Motion powered
- **Auto-Summarization** - Click email → Instant AI summary

### 🤖 AI Capabilities
- **Natural Language Processing** - Understands complex commands
- **Context-Aware Responses** - Remembers conversation flow
- **Smart Email Drafting** - Professional tone and formatting
- **Intelligent Summarization** - 3-bullet executive summaries
- **Multi-Tool Orchestration** - Chains multiple actions
- **Error Recovery** - Graceful handling of edge cases

### 📧 Email Management (15 Tools)

| Tool | Function | Example Command |
|------|----------|----------------|
| `fetch_emails` | Browse recent emails | "Show my latest 10 emails" |
| `send_email` | Send new emails | "Email john@example.com about meeting" |
| `count_unread` | Check unread count | "How many unread emails?" |
| `delete_email` | Delete emails | "Delete email 123" |
| `mark_as_read` | Mark as read | "Mark email 456 as read" |
| `mark_as_unread` | Mark as unread | "Mark email 789 as unread" |
| `search_emails` | Advanced search | "Find emails from john about project" |
| `get_email_details` | Full email content | "Show full content of email 123" |
| `reply_to_email` | Reply with threading | "Reply to email 456 with 'Thanks!'" |
| `forward_email` | Forward to others | "Forward email 789 to team@company.com" |
| `create_draft` | Save drafts | "Create draft to boss@company.com" |
| `archive_email` | Archive emails | "Archive email 234" |
| `star_email` | Star important emails | "Star email 567" |
| `extract_contacts` | Get contact list | "Extract my email contacts" |
| `schedule_email` | Schedule for later | "Schedule email for tomorrow 9am" |

---

## 📸 Screenshots

### Login Screen
- Sleek dark theme with gradient background
- Secure App Password authentication
- Modern form design with Sparkles icon

### Main Interface
- **Left Sidebar** (64px) - Navigation icons (Inbox, AI, Theme, Settings)
- **Center Panel** (Flexible) - Email list with hover effects
- **Right Panel** (450px) - AI Chat with real-time responses

### Email Modal
- **AI Summary Header** - Gradient background with instant insights
- **Full Email Content** - Markdown-rendered body
- **Action Buttons** - Reply with Agent, Close
- **Sender Avatar** - Color-coded initials

---

## 🚀 Installation

### Prerequisites
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Gmail Account** with 2-Step Verification
- **Gemini API Key** - [Get Free Key](https://aistudio.google.com/app/apikey)

### Quick Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd email-agent

# 2. Backend Setup
cd ai-email-assistant/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Frontend Setup
cd ../frontend
npm install

# 4. Return to root
cd ../..
```

---

## ⚙️ Configuration

### 1. Gmail App Password Setup

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Visit [App Passwords](https://myaccount.google.com/apppasswords)
4. Select **Mail** → Generate
5. Copy the **16-character password** (e.g., `abcd efgh ijkl mnop`)

### 2. Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key (starts with `AIza...`)

### 3. Application Configuration

**No .env files needed!** All credentials are entered via the UI:
- **Login Screen** → Gmail email + App Password
- **Settings Modal** → Gemini API Key

---

## 🎯 Running the Application

### Option 1: Quick Start (Recommended)

```bash
# From project root
start.bat
```
✅ Opens **both** backend and frontend automatically!

### Option 2: Individual Scripts

```bash
# Backend only (Port 8000)
start-backend.bat

# Frontend only (Port 5173)
start-frontend.bat
```

### Option 3: Manual Start

**Terminal 1 - Backend:**
```bash
cd ai-email-assistant/backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd ai-email-assistant/frontend
npm run dev
```

### Access URLs
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 💬 Using the AI Agent

### First Time Setup

1. **Login**
   - Open http://localhost:5173
   - Enter Gmail address
   - Enter App Password (16 characters, no spaces)
   - Click "Connect Agent"

2. **Configure AI**
   - Click Settings icon (⚙️) in sidebar
   - Paste Gemini API Key
   - Click "Save Configuration"

3. **Start Using**
   - Type commands in AI Chat panel (right side)
   - Click emails to view with auto-summary
   - Toggle dark/light theme (🌙/☀️)

### Example Commands

**Basic Operations:**
```
"Check my unread emails"
"Show me my latest 10 emails"
"How many unread messages do I have?"
"Refresh my inbox"
```

**Search & Filter:**
```
"Find emails from john@example.com"
"Search emails about 'meeting'"
"Show emails from last week"
"Find emails with 'invoice' in subject"
```

**Email Actions:**
```
"Delete email 123"
"Mark email 456 as read"
"Star email 789"
"Archive email 234"
"Mark all as read"
```

**Communication:**
```
"Send an email to boss@company.com about the project update"
"Reply to email 123 with 'Thanks for the update!'"
"Forward email 456 to team@company.com"
"Create a draft to client@example.com about proposal"
```

**Advanced:**
```
"Get full details of email 789"
"Extract my email contacts"
"Schedule email to john@example.com for tomorrow 9am"
"Summarize the last email"
"Draft a professional reply to the latest email"
```

### AI Conversation Memory

The AI remembers your last **15 exchanges** (30 messages):

```
You: "Check my latest email"
AI: [Shows email from John about meeting]

You: "Who sent that?"
AI: "John sent that email" ✅ Remembers context!

You: "Reply with 'I'll be there'"
AI: [Sends reply to John] ✅ Context-aware!
```

### Auto-Summarization Feature

**How it works:**
1. Click any email in the inbox
2. Modal opens with email content
3. AI **automatically generates** 3-bullet summary
4. Summary appears in gradient header
5. Full email body shown below

**No manual "Summarize" button needed!**

---

## 🛠️ Available Tools

### 1. `fetch_emails(limit, query)`
**Purpose:** Retrieve recent emails  
**Parameters:**
- `limit` (int): Number of emails (default: 10)
- `query` (str): Search term or "ALL"

**Example:** "Show me my latest 5 emails"

---

### 2. `send_email(to_email, subject, body)`
**Purpose:** Send a new email  
**Parameters:**
- `to_email` (str): Recipient address
- `subject` (str): Email subject
- `body` (str): Email content

**Example:** "Send email to john@example.com about meeting"

---

### 3. `count_unread()`
**Purpose:** Count unread emails  
**Parameters:** None

**Example:** "How many unread emails?"

---

### 4. `delete_email(email_id)`
**Purpose:** Delete an email  
**Parameters:**
- `email_id` (str): Email ID to delete

**Example:** "Delete email 123"

---

### 5. `mark_as_read(email_id)`
**Purpose:** Mark email as read  
**Parameters:**
- `email_id` (str): Email ID

**Example:** "Mark email 456 as read"

---

### 6. `mark_as_unread(email_id)`
**Purpose:** Mark email as unread  
**Parameters:**
- `email_id` (str): Email ID

**Example:** "Mark email 789 as unread"

---

### 7. `search_emails(sender, subject, date_from, date_to)`
**Purpose:** Advanced email search  
**Parameters:**
- `sender` (str): Filter by sender
- `subject` (str): Filter by subject
- `date_from` (str): Start date (DD-Mon-YYYY)
- `date_to` (str): End date (DD-Mon-YYYY)

**Example:** "Find emails from john@example.com about project"

---

### 8. `get_email_details(email_id)`
**Purpose:** Get full email content  
**Parameters:**
- `email_id` (str): Email ID

**Returns:** Full body, attachments list

**Example:** "Show me full content of email 123"

---

### 9. `reply_to_email(email_id, reply_body)`
**Purpose:** Reply to an email  
**Parameters:**
- `email_id` (str): Original email ID
- `reply_body` (str): Reply message

**Example:** "Reply to email 456 with 'Thanks!'"

---

### 10. `forward_email(email_id, to_email, message)`
**Purpose:** Forward an email  
**Parameters:**
- `email_id` (str): Email to forward
- `to_email` (str): Recipient
- `message` (str): Optional note

**Example:** "Forward email 789 to team@company.com"

---

### 11. `create_draft(to_email, subject, body)`
**Purpose:** Create email draft  
**Parameters:**
- `to_email` (str): Recipient
- `subject` (str): Subject
- `body` (str): Content

**Example:** "Create draft to boss@company.com about vacation"

---

### 12. `archive_email(email_id)`
**Purpose:** Archive email (remove from inbox)  
**Parameters:**
- `email_id` (str): Email ID

**Example:** "Archive email 234"

---

### 13. `star_email(email_id)`
**Purpose:** Star/flag important email  
**Parameters:**
- `email_id` (str): Email ID

**Example:** "Star email 567"

---

### 14. `extract_contacts(limit)`
**Purpose:** Extract unique contacts  
**Parameters:**
- `limit` (int): Emails to scan (default: 20)

**Example:** "Extract my email contacts"

---

### 15. `schedule_email(to_email, subject, body, send_time)`
**Purpose:** Schedule email for later  
**Parameters:**
- `to_email` (str): Recipient
- `subject` (str): Subject
- `body` (str): Content
- `send_time` (str): When to send

**Note:** Creates draft with scheduling note

**Example:** "Schedule email to john@example.com for tomorrow 9am"

---

## 🐛 Troubleshooting

### Login Issues

**Problem:** Login fails  
**Solution:**
- ✅ Ensure 2-Step Verification is enabled
- ✅ Use **App Password**, NOT regular password
- ✅ Remove spaces from App Password (16 chars)
- ✅ Check email address is correct
- ✅ Verify IMAP is enabled in Gmail settings

---

### AI Not Responding

**Problem:** AI doesn't respond or shows errors  
**Solution:**
- ✅ Check Gemini API key is valid
- ✅ Verify API key is saved in Settings
- ✅ Ensure backend is running (port 8000)
- ✅ Check browser console (F12) for errors
- ✅ Restart backend server

---

### Emails Not Loading

**Problem:** Inbox shows "No new emails"  
**Solution:**
- ✅ Click Inbox icon in sidebar
- ✅ Check Gmail App Password is correct
- ✅ Verify internet connection
- ✅ Check backend terminal for errors
- ✅ Restart both servers

---

### Auto-Summary Not Working

**Problem:** Email modal doesn't show AI summary  
**Solution:**
- ✅ Ensure Gemini API key is configured
- ✅ Check backend logs for API errors
- ✅ Verify email has content (not empty)
- ✅ Wait 2-3 seconds for AI generation
- ✅ Check API quota limits

---

### Theme Not Switching

**Problem:** Dark/Light mode toggle doesn't work  
**Solution:**
- ✅ Click Sun/Moon icon in sidebar
- ✅ Refresh browser (Ctrl + R)
- ✅ Clear browser cache
- ✅ Check localStorage in DevTools

---

## 🔧 Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 5173)                  │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Sidebar  │  │  Email List  │  │  AI Chat Panel  │  │
│  │  (64px)  │  │  (Flexible)  │  │     (450px)     │  │
│  └──────────┘  └──────────────┘  └─────────────────┘  │
│         React 18 + Vite 5 + Tailwind CSS               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST (Axios)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    BACKEND (Port 8000)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   FastAPI    │  │  Gemini AI   │  │  15 Tools    │ │
│  │   Routes     │  │  Integration │  │  Functions   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         Python 3.8+ + Uvicorn + Pydantic               │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│   Gmail IMAP     │  │   Gemini API     │
│   Gmail SMTP     │  │   (2.5 Flash)    │
│  (Port 993/465)  │  │  (ai.google.dev) │
└──────────────────┘  └──────────────────┘
```

### Tech Stack

**Frontend:**
- **React 18** - UI library
- **Vite 5** - Build tool & dev server
- **Tailwind CSS 3** - Utility-first styling
- **Framer Motion 10** - Smooth animations
- **Lucide React** - Modern icon set
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Remark GFM** - GitHub Flavored Markdown

**Backend:**
- **Python 3.8+** - Core language
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Google Generative AI** - Gemini 2.5 Flash
- **IMAP/SMTP** - Email protocols
- **Pydantic** - Data validation
- **Python-dotenv** - Environment management

### File Structure

```
email-agent/
├── ai-email-assistant/
│   ├── backend/
│   │   ├── main.py              # FastAPI server (1153 lines)
│   │   │   ├── 15 Tool Functions
│   │   │   ├── 7 API Endpoints
│   │   │   ├── Gemini AI Integration
│   │   │   └── Session Management
│   │   └── requirements.txt     # Python dependencies
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx          # Main React component (850 lines)
│       │   │   ├── State Management
│       │   │   ├── UI Components
│       │   │   ├── AI Chat Logic
│       │   │   └── Email Modal
│       │   ├── main.jsx         # React entry point
│       │   └── index.css        # Global styles + Tailwind
│       ├── package.json         # Node dependencies
│       ├── vite.config.js       # Vite configuration
│       └── tailwind.config.js   # Tailwind configuration
├── start.bat                    # Start both servers (Windows)
├── start-backend.bat            # Start backend only
├── start-frontend.bat           # Start frontend only
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore rules
```

### API Endpoints

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/auth/login` | POST | Login with Gmail | `{email, password}` |
| `/auth/logout` | POST | Logout and clear session | None |
| `/api/status` | GET | Check auth status | None |
| `/api/settings/gemini` | POST | Set Gemini API key | `{key}` |
| `/api/clear-history` | POST | Clear chat history | None |
| `/api/emails` | GET | Get emails list | None |
| `/api/agent` | POST | Send AI command | `{command, model, gemini_key}` |

### Security Features

- ✅ **App Passwords** - Safer than regular passwords
- ✅ **Session Storage** - API keys never touch disk
- ✅ **No .env Files** - All config via UI
- ✅ **CORS Protection** - Controlled origins
- ✅ **.gitignore** - Excludes sensitive files
- ✅ **HTTPS Ready** - SSL/TLS compatible
- ✅ **Input Validation** - Pydantic models

### Memory System

**Storage:** In-memory session dictionary  
**Capacity:** 30 messages (15 user + 15 AI)  
**Format:** `[{role: 'user', content: '...'}, ...]`  
**Persistence:** Until logout or server restart  
**Cleanup:** Automatic (FIFO, keeps last 30)  
**Access:** `active_session["chat_history"]`

### AI Model Configuration

**Model:** Gemini 2.5 Flash  
**Context Window:** 1M tokens  
**Function Calling:** Manual implementation  
**Error Handling:** 5-layer validation  
**Response Time:** ~2-5 seconds average  
**Max Iterations:** 5 (prevents infinite loops)  
**Temperature:** 0.7 (balanced creativity)

### UI/UX Features

**Theme System:**
- Dark mode (default) - Black/Zinc palette
- Light mode - Slate/White palette
- Persisted in localStorage
- Smooth transitions

**Layout:**
- Sidebar: 64px (icons only)
- Email List: Flexible width
- AI Chat: 450px (fixed)
- Email Modal: Max 90vh, centered

**Animations:**
- Framer Motion for modals
- Hover effects on emails
- Loading spinners
- Toast notifications

**Responsive:**
- Adapts to screen size
- Scrollable panels
- Custom scrollbars
- Mobile-friendly (planned)

---

## 📄 License

MIT License - Free to use for personal or commercial projects.

See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Powerful language model
- **FastAPI** - Excellent Python framework
- **React + Vite** - Modern frontend stack
- **Gmail IMAP/SMTP** - Email integration
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide Icons** - Beautiful icon set

---

## 📞 Support

### Common Issues
- Check [Troubleshooting](#-troubleshooting) section
- Review backend terminal logs
- Check browser console (F12)
- Verify API keys and credentials

### For Development
- **Backend API Docs:** http://localhost:8000/docs
- **Frontend Dev Tools:** F12 in browser
- **Hot Reload:** Both servers support auto-reload

### Debugging Tips
1. **Backend Errors:** Check terminal running `main.py`
2. **Frontend Errors:** Open browser DevTools (F12)
3. **API Issues:** Visit `/docs` for interactive testing
4. **Email Issues:** Verify Gmail IMAP/SMTP settings

---

## 🚀 Future Enhancements

- [ ] Email attachments download
- [ ] Rich text email composer
- [ ] Email templates
- [ ] Multi-account support
- [ ] Mobile responsive design
- [ ] Email search filters UI
- [ ] Keyboard shortcuts
- [ ] Email labels/folders
- [ ] Batch operations
- [ ] Export conversations

---

**Made with ❤️ using Google Gemini AI**

**Version:** 2.0.0  
**Last Updated:** December 2024  
**Status:** Production Ready ✅

---

## 🌟 Star This Project

If you find this project helpful, please consider giving it a ⭐ on GitHub!

**Happy Emailing! 📧🤖**
