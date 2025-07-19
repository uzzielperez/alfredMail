# Gmail API Setup Guide

## Step 1: Create a New Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" (top left, next to "Google Cloud")
3. Name your project (e.g., "Personal Email Assistant")
4. Click "Create"

## Step 2: Enable Gmail API

1. In your new project, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type → **Create**
3. Fill required fields:
   - **App name**: "Personal Email Assistant"
   - **User support email**: Your email
   - **Developer contact**: Your email
4. **Scopes**: Skip for now
5. **Test users**: 
   - Click "Add users"
   - Add your Gmail address
   - **This is crucial** - it allows you to use the app without verification
6. Click "Save and Continue" through all steps

## Step 4: Create Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Desktop application**
4. Name it "Email Assistant Desktop"
5. Click **Create**
6. **Download** the JSON file
7. **Rename** it to `client_credentials.json`
8. **Move** it to your project folder: `/Users/uzzielperez/Desktop/mktaiagent/`

## Step 5: Run Setup

```bash
python gmail_setup.py
```

This will:
- Open your browser for authentication
- Create the necessary credential files
- Set up your app to work with Gmail

## Important Notes

- ⚠️ The app will show a "Google hasn't verified this app" warning
- ✅ Click "Advanced" → "Go to Personal Email Assistant (unsafe)"
- ✅ This is safe since it's your own app
- ✅ Grant permissions for Gmail access

## Troubleshooting

If you still see verification errors:
1. Make sure you added yourself as a test user
2. Use the same Google account for both setup and testing
3. Clear browser cache and try again 