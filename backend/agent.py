import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from memory import save_message, get_history
from tools.gmail import read_emails, send_email
from tools.calendar import get_events, create_event, delete_event, update_event
from tools.search import web_search

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_system_prompt():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""You are Aria, a personal AI assistant living inside WhatsApp.
You are helpful, concise, and friendly. You speak naturally — like a smart friend, not a formal assistant.
Keep responses short and conversational. This is a chat interface, not a document.
You have memory of past conversations with the user.
You have access to the user's Gmail, Google Calendar, and the web.
You can read emails, send emails, check/create/update/delete calendar events, and search the web for current information.
If you don't know something, say so honestly. Never make up facts.

TODAY'S DATE: {today}
When creating calendar events, ALWAYS convert dates to ISO format: YYYY-MM-DDTHH:MM:SS
Examples: "tomorrow at 3pm" = "{today[:8]}{int(today[8:10])+1:02d}T15:00:00", "April 2 at 10am" = "2026-04-02T10:00:00"
NEVER pass natural language like "tomorrow" or "April 2 at 10am" as start/end — always convert first.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Read the latest 5 emails from the user's Gmail inbox",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email on behalf of the user via Gmail",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Email body text"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Get upcoming events from the user's Google Calendar for the next 7 days",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Create a new event in the user's Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start": {"type": "string", "description": "Start time in format YYYY-MM-DDTHH:MM:SS"},
                    "end": {"type": "string", "description": "End time in format YYYY-MM-DDTHH:MM:SS"},
                    "description": {"type": "string", "description": "Optional event description"}
                },
                "required": ["title", "start", "end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, news, weather, facts, or anything the AI doesn't know",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete a calendar event by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title (or part of title) of the event to delete"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "Update an existing calendar event — change its title, start time, or end time",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Current title of the event to update"},
                    "new_title": {"type": "string", "description": "New title (optional)"},
                    "new_start": {"type": "string", "description": "New start time in format YYYY-MM-DDTHH:MM:SS (optional)"},
                    "new_end": {"type": "string", "description": "New end time in format YYYY-MM-DDTHH:MM:SS (optional)"}
                },
                "required": ["title"]
            }
        }
    }
]


def execute_tool(name: str, args: dict) -> str:
    if name == 'read_emails':
        return read_emails()
    elif name == 'send_email':
        return send_email(args['to'], args['subject'], args['body'])
    elif name == 'get_events':
        return get_events()
    elif name == 'create_event':
        return create_event(args['title'], args['start'], args['end'], args.get('description', ''))
    elif name == 'web_search':
        return web_search(args['query'])
    elif name == 'delete_event':
        return delete_event(args['title'])
    elif name == 'update_event':
        return update_event(args['title'], args.get('new_start'), args.get('new_end'), args.get('new_title'))
    return f"Unknown tool: {name}"


def get_response(from_number: str, message: str) -> str:
    history = get_history(from_number)

    messages = [{'role': 'system', 'content': get_system_prompt()}]
    for msg in history:
        role = 'assistant' if msg['role'] == 'model' else msg['role']
        messages.append({'role': role, 'content': msg['parts'][0]['text']})
    messages.append({'role': 'user', 'content': message})

    response = client.chat.completions.create(
        model='llama3-8b-8192',
        messages=messages,
        tools=TOOLS,
        tool_choice='auto',
        max_tokens=500
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"[TOOL] Calling {tool_name} with {tool_args}")
            tool_result = execute_tool(tool_name, tool_args)
            print(f"[TOOL] Result: {tool_result[:100]}...")

            messages.append({
                'role': 'tool',
                'tool_call_id': tool_call.id,
                'content': tool_result
            })

        final_response = client.chat.completions.create(
            model='llama3-8b-8192',
            messages=messages,
            max_tokens=500
        )
        reply = final_response.choices[0].message.content

    else:
        reply = response_message.content

    save_message(from_number, 'user', message)
    save_message(from_number, 'model', reply)

    return reply
