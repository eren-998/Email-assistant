# 🤖 AI Email Agent

An intelligent email assistant powered by Google's Gemini AI that helps you manage your Gmail inbox through natural language conversations.

## ✨ Features

- 🔐 **Secure Gmail Integration** - Connect using App Passwords
- 💬 **AI-Powered Chat** - Natural language email management
- 📧 **Email Operations** - Read, draft, send, and manage emails
- 🎨 **Modern UI** - Clean blue & white interface
- 🚀 **Multiple AI Models** - Support for Gemini 2.0, 2.5, 1.5 Flash & Pro
- 📱 **Responsive Design** - Works on all screen sizes

## 🛠️ Tech Stack

**Frontend:**
- React + Vite
- Tailwind CSS
- Framer Motion (animations)
- Axios
- React Markdown

**Backend:**
- FastAPI (Python)
- Google Generative AI (Gemini)
- IMAP/SMTP for Gmail
- Uvicorn

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Gmail account with App Password enabled
- Gemini API key

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/email-agent.git
cd email-agent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your credentials
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## ⚙️ Configuration

### Get Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### Update .env File

Edit `backend/.env`:
```env
GEMINI_API_KEY=your_actual_gemini_key
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_password
```

## 🎯 Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Backend will run on: `http://localhost:8000`

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:5173`

## 📖 Usage

1. **Login**
   - Enter your Gmail address
   - Enter your App Password (16 characters)
   - Click "Sign In"

2. **Configure AI**
   - Click Settings icon
   - Enter your Gemini API Key
   - Select AI model (Gemini 2.0 Flash recommended)
   - Click "Save Settings"

3. **Start Chatting**
   - Type commands in the chat box
   - Examples:
     - "Check my unread emails"
     - "Summarize my latest emails"
     - "Draft an email to john@example.com about the meeting"
     - "How many unread messages do I have?"

## 🎨 UI Layout

- **Top Half**: AI Chat Interface
- **Bottom Half**: Email Inbox (grid view)
- **Blue & White Theme**: Clean, professional design

## 🔒 Security Notes

- Never commit `.env` files to Git
- App Passwords are safer than regular passwords
- API keys are stored server-side only
- All credentials are excluded via `.gitignore`

## 📝 Available AI Models

- **Gemini 2.0 Flash** (Recommended) - Fast and efficient
- **Gemini 2.5 Flash** - Latest experimental model
- **Gemini 1.5 Flash** - Stable and reliable
- **Gemini 1.5 Pro** - Most capable, slower

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🐛 Troubleshooting

**Login fails:**
- Ensure 2-Step Verification is enabled
- Use App Password, not regular password
- Check email address is correct

**AI not responding:**
- Verify Gemini API key is valid
- Check API key is saved in Settings
- Ensure backend is running

**Emails not loading:**
- Check Gmail App Password is correct
- Verify IMAP is enabled in Gmail settings
- Check internet connection

## 👨‍💻 Author

Created with ❤️ using Google Gemini AI

## 🌟 Acknowledgments

- Google Gemini AI for the powerful language model
- FastAPI for the excellent Python framework
- React team for the amazing frontend library
