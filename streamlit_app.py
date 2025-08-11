import streamlit as st
import os
import json
from groq import Groq
from gmail_api import (
    get_unread_emails,
    send_email_reply,
    get_gmail_service,
    load_knowledge_base,
    find_relevant_knowledge,
    update_knowledge_base
)
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="AI Email Assistant", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
<style>
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .email-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📬 AI Email Assistant")
st.markdown("### Manage your Gmail with AI-powered assistance")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'emails' not in st.session_state:
    st.session_state.emails = []

# Check for Groq API key
if "groq_api_key" in st.secrets:
    groq_client = Groq(api_key=st.secrets["groq_api_key"])
else:
    groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
    else:
        st.warning("Please enter your Groq API key in the sidebar to enable AI features.")
        groq_client = None

# Authentication status check
def check_gmail_auth():
    """Check if Gmail is authenticated"""
    try:
        service = get_gmail_service()
        return True
    except:
        return False

# Sidebar for authentication
with st.sidebar:
    st.header("🔐 Authentication")

    if check_gmail_auth():
        st.success("✅ Gmail Connected")
        st.session_state.authenticated = True

        if st.button("🔄 Refresh Authentication"):
            # Clear existing credentials to force re-auth
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
            st.rerun()
    else:
        st.warning("⚠️ Gmail Not Connected")
        st.session_state.authenticated = False

        st.markdown("**Setup Gmail Access:**")
        st.markdown("1. Ensure `client_credentials.json` is in your project folder")
        st.markdown("2. Run the setup script:")
        st.code("python gmail_setup.py")
        st.markdown("3. Refresh this page")

        if st.button("🔄 Check Connection"):
            st.rerun()

    # Sidebar for Knowledge Base Management
    with st.sidebar:
        st.header("📚 Knowledge Base")
        st.markdown("Drag and drop a JSON file here to add new Q&A pairs to your knowledge base.")
        
        uploaded_file = st.file_uploader(
            "Upload Knowledge Base File", 
            type=['json'], 
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                # Read and decode the uploaded file
                new_entries = json.load(uploaded_file)
                
                # Basic validation to ensure it's a list of dictionaries
                if isinstance(new_entries, list) and all(isinstance(e, dict) for e in new_entries):
                    added_count = update_knowledge_base(new_entries)
                    st.success(f"✅ Knowledge base updated! Added {added_count} new entries.")
                    st.toast("File processed successfully!", icon="🎉")
                else:
                    st.error("❌ Invalid format. The JSON file must contain a list of objects, each with a 'question' and 'answer' key.")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please check the file format.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Main content area
if st.session_state.authenticated:
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("📥 Load Unread Emails", use_container_width=True):
            with st.spinner("Connecting to Gmail and fetching unread emails..."):
                try:
                    emails = get_unread_emails()
                    st.session_state.emails = emails
                    st.success(f"✅ Fetched {len(emails)} unread email(s)")
                except Exception as e:
                    st.error(f"❌ Error connecting to Gmail: {str(e)}")

    with col2:
        if st.session_state.emails:
            st.metric("Unread Emails", len(st.session_state.emails))
else:
    st.info("🔐 Please authenticate with Gmail first using the sidebar instructions.")

# Display emails
if st.session_state.authenticated and st.session_state.emails:
    st.header(f"📧 Unread Emails ({len(st.session_state.emails)})")

    # Add a global "Auto-Reply" button for selected emails
    if groq_client:
        st.info("💡 **Pro-Tip:** Select multiple emails and click the button below to generate all drafts at once!")
        if st.button("🤖 Generate Draft Replies for Selected Emails", use_container_width=True):

            selected_indices = [
                i for i, email in enumerate(st.session_state.emails)
                if st.session_state.get(f"select_{i}", False)
            ]

            if not selected_indices:
                st.warning("⚠️ Please select at least one email first.")
            else:
                progress_bar = st.progress(0, text="Generating drafts...")
                total_selected = len(selected_indices)

                for i, idx in enumerate(selected_indices):
                    email = st.session_state.emails[idx]
                    try:
                        with st.spinner(f"Drafting reply for: {email['subject'][:50]}..."):
                            response = groq_client.chat.completions.create(
                                model="llama3-70b-8192",
                                messages=[
                                    {"role": "user", "content": f"Draft a professional and helpful reply to this email. Be concise and friendly:\n\nOriginal email:\n{email['body']}"}
                                ]
                            )
                            draft = response.choices[0].message.content
                            st.session_state[f"draft_{idx}"] = draft
                    except Exception as e:
                        st.error(f"Error drafting reply for email from {email['sender']}: {str(e)}")

                    # Update progress bar
                    progress_bar.progress((i + 1) / total_selected, text=f"Generated {i+1}/{total_selected} drafts")

                st.success(f"✅ Successfully generated {total_selected} drafts!")
                st.balloons()

    st.markdown("---")

    # Loop through emails and display them with a checkbox
    for idx, email in enumerate(st.session_state.emails):

        col1, col2 = st.columns([0.05, 0.95])

        with col1:
            st.checkbox("", key=f"select_{idx}", label_visibility="collapsed")

        with col2:
            with st.expander(f"**{email['subject']}** from {email['sender']}", expanded=False):
                # Email header info
                h_col1, h_col2 = st.columns(2)
                with h_col1:
                    st.markdown(f"**From:** {email['sender']}")
                with h_col2:
                    st.markdown(f"**Date:** {email['date']}")

                # Email body
                st.markdown("**Email Content:**")
                st.text_area("", value=email['body'], height=200, key=f"email_body_{idx}", disabled=True)

                # AI Features
                if groq_client:
                    ai_col1, ai_col2 = st.columns(2)

                    with ai_col1:
                        if st.button(f"🧠 Summarize", key=f"summarize_btn_{idx}", use_container_width=True):
                            with st.spinner("Generating summary..."):
                                try:
                                    response = groq_client.chat.completions.create(
                                        model="llama3-70b-8192",
                                        messages=[
                                            {"role": "user", "content": f"Provide a concise summary of this email in 2-3 sentences:\n\n{email['body']}"}
                                        ]
                                    )
                                    summary = response.choices[0].message.content
                                    st.success("📝 **Summary:**")
                                    st.write(summary)
                                except Exception as e:
                                    st.error(f"Error generating summary: {str(e)}")

                    with ai_col2:
                        # Individual draft button remains
                        if st.button(f"✨ Draft Reply", key=f"draft_btn_{idx}", use_container_width=True):
                            with st.spinner("Drafting reply..."):
                                try:
                                    response = groq_client.chat.completions.create(
                                        model="llama3-70b-8192",
                                        messages=[
                                            {"role": "user", "content": f"Draft a professional and helpful reply to this email. Be concise and friendly:\n\nOriginal email:\n{email['body']}"}
                                        ]
                                    )
                                    draft = response.choices[0].message.content
                                    st.session_state[f"draft_{idx}"] = draft
                                except Exception as e:
                                    st.error(f"Error drafting reply: {str(e)}")

                # RAG Feature: Draft from Knowledge Base
                if groq_client:
                    if st.button("📚 Draft from Knowledge Base", key=f"rag_btn_{idx}", use_container_width=True):
                        knowledge_base = load_knowledge_base()
                        if not knowledge_base:
                            st.warning("⚠️ Knowledge base is empty or not found. Please create `knowledge_base.json`.")
                        else:
                            with st.spinner("Searching knowledge base and drafting reply..."):
                                relevant_info = find_relevant_knowledge(email['body'], knowledge_base)

                                if not relevant_info:
                                    st.info("No relevant information found in the knowledge base for this email.")
                                else:
                                    # Prepare a prompt for Groq that includes the relevant context
                                    context = "\n\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in relevant_info])
                                    prompt = (
                                        f"You are an AI assistant. Use the following context from our knowledge base to draft a reply to the email below. "
                                        f"Be professional, helpful, and friendly. If the context is not sufficient to answer the question, politely say so.\n\n"
                                        f"--- Knowledge Base Context ---\n{context}\n\n"
                                        f"--- Original Email ---\n{email['body']}"
                                    )

                                    try:
                                        response = groq_client.chat.completions.create(
                                            model="llama3-70b-8192",
                                            messages=[{"role": "user", "content": prompt}]
                                        )
                                        draft = response.choices[0].message.content
                                        st.session_state[f"draft_{idx}"] = draft
                                        st.success("✅ Draft generated from knowledge base!")
                                    except Exception as e:
                                        st.error(f"Error generating RAG reply: {str(e)}")

                # Reply section
                st.markdown("---")
                st.markdown("**✏️ Your Reply:**")

                initial_reply = st.session_state.get(f"draft_{idx}", "")
                reply = st.text_area("", value=initial_reply, height=150, key=f"reply_{idx}", placeholder="Type your reply here or generate one...")

                send_col1, send_col2 = st.columns([1, 3])
                with send_col1:
                    if st.button(f"📤 Send Reply", key=f"send_reply_btn_{idx}", use_container_width=True):
                        if reply.strip():
                            try:
                                send_email_reply(
                                    to=email['sender'],
                                    subject="Re: " + email['subject'],
                                    body=reply,
                                    thread_id=email['thread_id']
                                )
                                st.success("✅ Reply sent successfully!")
                                st.session_state[f"reply_{idx}"] = ""
                            except Exception as e:
                                st.error(f"❌ Error sending reply: {str(e)}")
                        else:
                            st.warning("Please write a reply before sending.")

elif st.session_state.authenticated and not st.session_state.emails:
    st.info("📭 No unread emails to display. Click 'Load Unread Emails' to refresh.")

elif not st.session_state.authenticated:
    st.markdown("""
    ### 🚀 Welcome to AI Email Assistant!

    This app helps you manage your Gmail with AI-powered features:
    - 📥 **Load unread emails** from your Gmail inbox
    - 🧠 **AI summaries** of email content
    - ✨ **Auto-draft replies** using AI
    - 📤 **Send replies** directly from the app

    **Get Started:**
    1. Follow the authentication steps in the sidebar
    2. Load your unread emails
    3. Use AI features to manage your inbox efficiently!
    """)
