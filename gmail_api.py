import os
import pickle
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import base64
import email

def get_gmail_service():
    """Get Gmail service with proper authentication"""
    creds = None
    
    # Try to load from token.pickle first
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no token.pickle, try credentials.json
    elif os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file("credentials.json", scopes=["https://www.googleapis.com/auth/gmail.modify"])
    
    # If credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    if not creds:
        raise FileNotFoundError(
            "No Gmail credentials found. Please run 'python gmail_setup.py' first to authenticate."
        )
    
    service = build("gmail", "v1", credentials=creds)
    return service

def get_unread_emails():
    service = get_gmail_service()
    result = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = result.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        payload = msg_data['payload']
        parts = payload.get('parts', [payload.get('body', {})])

        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        date = next((h['value'] for h in headers if h['name'] == 'Date'), "Unknown Date")
        thread_id = msg_data['threadId']

        # Decode message body
        body_data = ''
        for part in parts:
            if 'body' in part and 'data' in part['body']:
                body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

        emails.append({
            "sender": sender,
            "subject": subject,
            "date": date,
            "body": body_data,
            "thread_id": thread_id
        })
    return emails

def send_email_reply(to, subject, body, thread_id):
    service = get_gmail_service()
    message = f"To: {to}\r\nSubject: {subject}\r\nIn-Reply-To: {thread_id}\r\n\r\n{body}"
    raw = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
    message = {
        'raw': raw,
        'threadId': thread_id
    }
    service.users().messages().send(userId='me', body=message).execute()

