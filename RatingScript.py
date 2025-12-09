"""
Outlook Calendar Event Retriever
Pulls all event details from your Outlook calendar using Microsoft Graph API
"""

import requests
import json
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication

# Configuration - Replace these with your Azure AD app credentials
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
TENANT_ID = 'your_tenant_id_here'
USER_EMAIL = 'your_email@example.com'

# Microsoft Graph API endpoint
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def get_access_token():
    """Authenticate and get access token using client credentials flow"""
    authority = f'https://login.microsoftonline.com/{TENANT_ID}'
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )
    
    # Request token with appropriate scope
    result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    
    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception(f"Failed to get token: {result.get('error_description', 'Unknown error')}")

def get_calendar_events(access_token, days_ahead=30):
    """Retrieve calendar events from Outlook"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Set date range for events
    start_date = datetime.now().isoformat()
    end_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
    
    # Build the API request URL with filters
    url = f"{GRAPH_API_ENDPOINT}/users/{USER_EMAIL}/calendar/calendarView"
    params = {
        'startDateTime': start_date,
        'endDateTime': end_date,
        '$top': 100,  # Maximum events per page
        '$select': 'subject,start,end,location,organizer,attendees,body,isAllDay,importance,sensitivity,categories'
    }
    
    all_events = []
    
    # Handle pagination
    while url:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_events.extend(data.get('value', []))
            
            # Get next page URL if it exists
            url = data.get('@odata.nextLink')
            params = None  # Params are included in nextLink
        else:
            raise Exception(f"Failed to retrieve events: {response.status_code} - {response.text}")
    
    return all_events

def format_event(event):
    """Format event data for display"""
    formatted = {
        'Subject': event.get('subject', 'No Subject'),
        'Start': event.get('start', {}).get('dateTime', 'N/A'),
        'End': event.get('end', {}).get('dateTime', 'N/A'),
        'Location': event.get('location', {}).get('displayName', 'No Location'),
        'Organizer': event.get('organizer', {}).get('emailAddress', {}).get('name', 'N/A'),
        'Is All Day': event.get('isAllDay', False),
        'Importance': event.get('importance', 'normal'),
        'Categories': event.get('categories', []),
        'Body Preview': event.get('body', {}).get('content', '')[:100] + '...' if event.get('body', {}).get('content') else 'No description'
    }
    
    # Format attendees
    attendees = event.get('attendees', [])
    formatted['Attendees'] = [
        f"{att.get('emailAddress', {}).get('name', 'Unknown')} ({att.get('type', 'unknown')})"
        for att in attendees
    ]
    
    return formatted

def main():
    """Main function to retrieve and display calendar events"""
    try:
        print("Authenticating with Microsoft Graph API...")
        token = get_access_token()
        
        print("Retrieving calendar events...")
        events = get_calendar_events(token, days_ahead=30)
        
        print(f"\n{'='*80}")
        print(f"Found {len(events)} events in the next 30 days")
        print(f"{'='*80}\n")
        
        for i, event in enumerate(events, 1):
            formatted = format_event(event)
            print(f"Event #{i}:")
            print(f"  Subject: {formatted['Subject']}")
            print(f"  Start: {formatted['Start']}")
            print(f"  End: {formatted['End']}")
            print(f"  Location: {formatted['Location']}")
            print(f"  Organizer: {formatted['Organizer']}")
            print(f"  All Day: {formatted['Is All Day']}")
            print(f"  Importance: {formatted['Importance']}")
            print(f"  Categories: {', '.join(formatted['Categories']) if formatted['Categories'] else 'None'}")
            print(f"  Attendees: {', '.join(formatted['Attendees']) if formatted['Attendees'] else 'None'}")
            print(f"  Description: {formatted['Body Preview']}")
            print(f"{'-'*80}\n")
        
        # Optional: Save to JSON file
        with open('outlook_events.json', 'w') as f:
            json.dump(events, f, indent=2)
        print(f"Events saved to 'outlook_events.json'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
