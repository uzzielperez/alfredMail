import os
import pickle
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import base64
import email
import json

def load_knowledge_base(file_path="knowledge_base.json"):
    """Load the knowledge base from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def find_relevant_knowledge(email_body, knowledge_base):
    """
    Find the most relevant knowledge base entries for a given email body.
    This is a simple implementation; more advanced versions could use NLP for semantic search.
    """
    email_lower = email_body.lower()
    relevant_knowledge = []
    
    for entry in knowledge_base:
        question_lower = entry['question'].lower()
        # Simple keyword matching; works well for FAQs
        if any(keyword in email_lower for keyword in question_lower.split()):
            relevant_knowledge.append(entry)
            
    return relevant_knowledge

def update_knowledge_base(new_entries, file_path="knowledge_base.json"):
    """Loads, updates, and saves the knowledge base, avoiding duplicates."""
    existing_knowledge = load_knowledge_base(file_path)
    
    # Use a dictionary to easily check for existing questions
    existing_questions = {entry['question'].lower().strip(): entry for entry in existing_knowledge}
    
    added_count = 0
    for new_entry in new_entries:
        question = new_entry.get('question', '')
        if question:
            question_lower = question.lower().strip()
            if question_lower not in existing_questions:
                existing_knowledge.append(new_entry)
                existing_questions[question_lower] = new_entry
                added_count += 1
            
    # Save the updated knowledge base with pretty printing
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_knowledge, f, indent=2, ensure_ascii=False)
        
    return added_count

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

