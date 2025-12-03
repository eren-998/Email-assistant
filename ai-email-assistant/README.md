# AI Email Assistant

## Setup Instructions

1. **Google Cloud Console Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.
   - Enable the **Gmail API**.
   - Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
   - Choose **Desktop app** (or Web application, but for this local setup, Desktop is fine, or Web with `http://localhost:8000/auth/callback` as redirect URI).
   - Download the JSON file.
   - Rename it to `credentials.json` and place it in the `backend` folder.

2. **Running the App**:
   - The app should be running already.
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`

3. **Usage**:
   - Click "Connect Gmail" on the dashboard.
   - Grant permissions.
   - Start chatting with your AI assistant!
