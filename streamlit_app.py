import streamlit as st
from groq import Groq
from gmail_api import get_unread_emails, send_email_reply

st.set_page_config(page_title="AI Email Assistant", layout="wide")
st.title("📬 AI Email Assistant")

# Initialize Groq client
groq_client = Groq(api_key=st.secrets["groq_api_key"])

# Load unread emails
if st.button("📥 Load Unread Emails"):
    with st.spinner("Connecting to Gmail and fetching unread emails..."):
        try:
            emails = get_unread_emails()
            st.session_state.emails = emails
            st.success(f"Fetched {len(emails)} unread email(s)")
        except FileNotFoundError as e:
            st.error("❌ Gmail API not set up yet!")
            st.info("📋 **Setup Instructions:**")
            st.write("1. Run `python gmail_setup.py` in your terminal")
            st.write("2. Follow the authentication steps")
            st.write("3. Come back and try again")
            st.code("python gmail_setup.py")
        except Exception as e:
            st.error(f"Error connecting to Gmail: {str(e)}")
            st.info("Make sure you've completed the Gmail API setup.")

# Display emails
if "emails" in st.session_state:
    for idx, email in enumerate(st.session_state.emails):
        with st.expander(f"📧 {email['subject']} — from {email['sender']}"):
            st.markdown(f"**From:** {email['sender']}")
            st.markdown(f"**Date:** {email['date']}")
            st.text_area("Email Body", value=email['body'], height=200, key=f"email_body_{idx}")

            if st.button(f"Summarize Email #{idx}", key=f"summarize_btn_{idx}"):
                with st.spinner("Summarizing..."):
                    response = groq_client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[
                            {"role": "user", "content": f"Summarize this email:\n\n{email['body']}"}
                        ]
                    )
                    summary = response.choices[0].message.content
                    st.text_area("🧠 Summary", value=summary, height=100, key=f"summary_{idx}")

            reply = st.text_area(f"✏️ Draft a reply to #{idx}", key=f"reply_{idx}")
            if st.button(f"Send Reply #{idx}", key=f"send_reply_btn_{idx}"):
                send_email_reply(
                    to=email['sender'],
                    subject="Re: " + email['subject'],
                    body=reply,
                    thread_id=email['thread_id']
                )
                st.success("Reply sent!")
