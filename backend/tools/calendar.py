import os
from datetime import datetime, timezone
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
    """Authenticate and return a Calendar service object.
    Reuses the same token.json as Gmail.
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

    return build('calendar', 'v3', credentials=creds)


def get_events(days: int = 7) -> str:
    """Get upcoming calendar events for the next N days."""
    try:
        service = get_service()

        now = datetime.now(timezone.utc)
        from datetime import timedelta
        end = now + timedelta(days=days)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return f'No events in the next {days} days.'

        lines = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date', ''))
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            loc_str = f' @ {location}' if location else ''
            lines.append(f"• {summary}{loc_str} — {start}")

        return f"Upcoming events ({days} days):\n" + "\n".join(lines)

    except Exception as e:
        return f"Error reading calendar: {str(e)}"


def create_event(title: str, start: str, end: str, description: str = '') -> str:
    """Create a calendar event.

    start/end format: 'YYYY-MM-DDTHH:MM:SS' (e.g. '2026-04-01T14:00:00')
    """
    try:
        service = get_service()

        event = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start, 'timeZone': 'Asia/Beirut'},
            'end': {'dateTime': end, 'timeZone': 'Asia/Beirut'},
        }

        created = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event '{title}' created on {start}."

    except Exception as e:
        return f"Error creating event: {str(e)}"


def delete_event(title: str) -> str:
    """Delete a calendar event by title (deletes the next upcoming match)."""
    try:
        service = get_service()
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        end = now + timedelta(days=30)

        results = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = results.get('items', [])
        for event in events:
            if title.lower() in event.get('summary', '').lower():
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                return f"Event '{event['summary']}' deleted."

        return f"No upcoming event found with title containing '{title}'."

    except Exception as e:
        return f"Error deleting event: {str(e)}"


def update_event(title: str, new_start: str = None, new_end: str = None, new_title: str = None) -> str:
    """Update an existing calendar event by title.

    Finds the next upcoming event matching title and updates it.
    """
    try:
        service = get_service()
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        end = now + timedelta(days=30)

        results = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = results.get('items', [])
        for event in events:
            if title.lower() in event.get('summary', '').lower():
                if new_title:
                    event['summary'] = new_title
                if new_start:
                    event['start'] = {'dateTime': new_start, 'timeZone': 'Asia/Beirut'}
                if new_end:
                    event['end'] = {'dateTime': new_end, 'timeZone': 'Asia/Beirut'}

                service.events().update(
                    calendarId='primary',
                    eventId=event['id'],
                    body=event
                ).execute()

                return f"Event '{title}' updated successfully."

        return f"No upcoming event found with title containing '{title}'."

    except Exception as e:
        return f"Error updating event: {str(e)}"
