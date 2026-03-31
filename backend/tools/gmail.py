import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_service():
    """Authenticate with Gmail and return a service object.

    First run: opens browser for Google login, saves token.json
    After that: uses saved token.json automatically
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def read_emails(count: int = 5) -> str:
    """Read the latest emails from inbox and return as formatted text."""
    try:
        service = get_service()
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=count
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return 'Your inbox is empty.'

        emails = []
        for msg in messages:
            detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in detail['payload']['headers']}
            snippet = detail.get('snippet', '')[:150]

            emails.append(
                f"From: {headers.get('From', 'Unknown')}\n"
                f"Subject: {headers.get('Subject', 'No subject')}\n"
                f"Date: {headers.get('Date', '')}\n"
                f"Preview: {snippet}"
            )

        return f"Here are your latest {len(emails)} emails:\n\n" + "\n\n---\n\n".join(emails)

    except Exception as e:
        return f"Error reading emails: {str(e)}"


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail."""
    try:
        service = get_service()

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        return f"Email sent to {to} with subject '{subject}'."

    except Exception as e:
        return f"Error sending email: {str(e)}"
