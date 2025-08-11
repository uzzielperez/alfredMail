# 🚀 Web App Deployment Guide

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Gmail API:**
   ```bash
   python gmail_setup.py
   ```

3. **Add your Groq API key:**
   - Edit `.streamlit/secrets.toml`
   - Add: `groq_api_key = "your_actual_api_key"`

4. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Add secrets in the Streamlit Cloud dashboard:
     - `groq_api_key = "your_key"`

3. **Note:** Gmail authentication requires manual setup on first use since OAuth flows need user interaction.

### Option 2: Heroku

1. **Create Procfile:**
   ```
   web: sh setup.sh && streamlit run streamlit_app.py
   ```

2. **Create setup.sh:**
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   port = $PORT
   enableCORS = false
   headless = true
   " > ~/.streamlit/config.toml
   ```

### Option 3: Docker

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "streamlit_app.py"]
   ```

## Important Notes

- **Gmail OAuth:** The first time a user runs the app, they need to complete Gmail OAuth flow
- **Credentials:** The `client_credentials.json` file should be included in your deployment
- **Security:** Never commit API keys or credentials to version control
- **Session State:** User sessions are maintained within the app for better UX

## Features

✅ **Modern Web UI** with responsive design  
✅ **Real-time Gmail integration**  
✅ **AI-powered email summaries**  
✅ **Auto-draft replies**  
✅ **Session state management**  
✅ **Error handling and user feedback**  
✅ **Mobile-friendly interface**  

## Troubleshooting

- **Gmail Auth Issues:** Delete `token.pickle` and re-authenticate
- **API Errors:** Check your Groq API key in secrets
- **Port Issues:** Streamlit runs on port 8501 by default
