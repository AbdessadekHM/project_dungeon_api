import json
import os
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.db.models import Q
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.models import User
from apps.management.models import Project
from apps.management.permissions import IsProjectOwnerOrCollaborator

from .models import Event, GoogleToken
from .serializers import EventSerializer

# Path to client secret file
CLIENT_SECRET_FILE = os.path.join(settings.BASE_DIR, 'client_secret_638463039976-keta1bha3nj6ekrp0gbt5ef9mnlbsrmj.apps.googleusercontent.com.json')

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]


def get_flow(redirect_uri=None):
    """Create and return a Google OAuth2 Flow instance."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI,
    )
    return flow


def get_credentials_from_token(google_token):
    """Build Credentials object from stored GoogleToken."""
    with open(CLIENT_SECRET_FILE, 'r') as f:
        client_config = json.load(f)['web']

    creds = Credentials(
        token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        token_uri=client_config['token_uri'],
        client_id=client_config['client_id'],
        client_secret=client_config['client_secret'],
        scopes=SCOPES,
    )
    return creds


def get_calendar_service(user):
    """Build a Google Calendar API service for the given user."""
    try:
        google_token = GoogleToken.objects.get(user=user)
    except GoogleToken.DoesNotExist:
        return None

    credentials = get_credentials_from_token(google_token)

    # If token is expired, refresh it
    if credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request
        credentials.refresh(Request())
        # Update stored token
        google_token.access_token = credentials.token
        if credentials.expiry:
            google_token.token_expiry = credentials.expiry
        google_token.save()

    return build('calendar', 'v3', credentials=credentials)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrCollaborator]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Event.objects.all()
        
        # Events associated with projects the user is involved in
        return Event.objects.filter(
            Q(project__owner=user) | 
            Q(project__collaborators=user) | 
            Q(project__teams__collaborators=user)
        ).distinct()


class GoogleAuthURLView(APIView):
    """Returns the Google OAuth2 authorization URL."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flow = get_flow()
        
        # Enable PKCE (Proof Key for Code Exchange)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
        )
        
        # Return the code_verifier directly to the frontend to handle stateless PKCE
        return Response({
            'authorization_url': authorization_url,
            'state': state,
            'code_verifier': getattr(flow, 'code_verifier', None)
        })


class GoogleAuthCallbackView(APIView):
    """Exchanges the auth code for tokens and stores them."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        # Expect the frontend to send us the verifier it saved
        code_verifier = request.data.get('code_verifier') 

        if not code:
            return Response(
                {'error': 'Authorization code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            flow = get_flow()
            
            # Fetch token with or without PKCE depending on what we received
            if code_verifier:
                flow.fetch_token(code=code, code_verifier=code_verifier)
            else:
                flow.fetch_token(code=code)
                
            credentials = flow.credentials

            # Calculate token expiry
            token_expiry = None
            if credentials.expiry:
                token_expiry = credentials.expiry

            # Store or update the token
            GoogleToken.objects.update_or_create(
                user=request.user,
                defaults={
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token or '',
                    'token_expiry': token_expiry,
                }
            )

            return Response({'message': 'Google Calendar connected successfully'})

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("this is from line 151")
            return Response(
                {'error': f'Failed to exchange code: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )



class GoogleConnectionStatusView(APIView):
    """Check if the user has connected their Google Calendar."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            google_token = GoogleToken.objects.get(user=request.user)
            return Response({
                'connected': True,
                'connected_at': google_token.created_at,
            })
        except GoogleToken.DoesNotExist:
            return Response({'connected': False})

    def delete(self, request):
        """Disconnect Google Calendar."""
        try:
            GoogleToken.objects.filter(user=request.user).delete()
            return Response({'message': 'Google Calendar disconnected'})
        except Exception as e:
            return Response(
                {'error': f'Failed to disconnect: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class GoogleCalendarSyncView(APIView):
    """Fetch events from user's Google Calendar."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = get_calendar_service(request.user)
        if not service:
            return Response(
                {'error': 'Google Calendar not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get time range from query params or default to current month
            time_min = request.query_params.get('time_min')
            time_max = request.query_params.get('time_max')

            if not time_min:
                now = datetime.now(timezone.utc)
                time_min = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            if not time_max:
                now = datetime.now(timezone.utc)
                # Last day in 1 year from now approx
                time_max = (now + timedelta(days=365)).replace(hour=23, minute=59, second=59).isoformat()

            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=250,
                singleEvents=True,
                orderBy='startTime',
            ).execute()

            google_events = events_result.get('items', [])

            # Format events for the frontend
            formatted_events = []
            for event in google_events:
                start = event.get('start', {})
                end = event.get('end', {})

                formatted_event = {
                    'id': event.get('id'),
                    'google_event_id': event.get('id'),
                    'title': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start.get('dateTime', start.get('date')),
                    'end': end.get('dateTime', end.get('date')),
                    'meet_link': event.get('hangoutLink', ''),
                    'attendees': [
                        {
                            'email': att.get('email'),
                            'responseStatus': att.get('responseStatus'),
                        }
                        for att in event.get('attendees', [])
                    ],
                    'event_type': 'meeting' if event.get('hangoutLink') else 'other',
                    'source': 'google',
                }
                formatted_events.append(formatted_event)

            return Response(formatted_events)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to fetch calendar events: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleCalendarCreateEventView(APIView):
    """Create an event in Google Calendar with optional Meet link."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        service = get_calendar_service(request.user)
        if not service:
            return Response(
                {'error': 'Google Calendar not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            title = request.data.get('title', 'Untitled Event')
            description = request.data.get('description', '')
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')
            create_meet = request.data.get('create_meet', False)
            attendee_ids = request.data.get('attendees', [])
            event_type = request.data.get('event_type', 'meeting')
            project_id = request.data.get('project')

            if not start_time or not end_time:
                return Response(
                    {'error': 'start_time and end_time are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not project_id:
                return Response({'error': 'project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return Response({'error': 'Invalid project ID'}, status=status.HTTP_400_BAD_REQUEST)

            # Build attendees list from user IDs
            attendees_list = []
            if attendee_ids:
                users = User.objects.filter(id__in=attendee_ids)
                attendees_list = [{'email': user.email} for user in users]

            # Build Google Calendar event body
            event_body = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
                'attendees': attendees_list,
            }

            # Add Google Meet conference if requested
            if create_meet:
                event_body['conferenceData'] = {
                    'createRequest': {
                        'requestId': f'meet-{datetime.now().timestamp()}',
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    }
                }

            # Create the event in Google Calendar
            created_event = service.events().insert(
                calendarId='primary',
                body=event_body,
                conferenceDataVersion=1 if create_meet else 0,
                sendUpdates='all',
            ).execute()

            meet_link = created_event.get('hangoutLink', '')

            # Also save the event in our local database
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            local_event = Event.objects.create(
                title=title,
                description=description,
                start_date=start_dt.date(),
                end_date=end_dt.date(),
                start_time=start_dt,
                end_time=end_dt,
                google_event_id=created_event.get('id'),
                meet_link=meet_link,
                project=project,
                assignee=request.user,
                deadline=end_dt.date(),
                status='todo',
                priority='medium',
                task_type='other',
            )

            if attendee_ids:
                local_event.attendees.set(attendee_ids)

            return Response({
                'id': created_event.get('id'),
                'title': created_event.get('summary'),
                'description': created_event.get('description', ''),
                'start': created_event.get('start', {}).get('dateTime'),
                'end': created_event.get('end', {}).get('dateTime'),
                'meet_link': meet_link,
                'attendees': [
                    {
                        'email': att.get('email'),
                        'responseStatus': att.get('responseStatus'),
                    }
                    for att in created_event.get('attendees', [])
                ],
                'source': 'google',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to create event: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
