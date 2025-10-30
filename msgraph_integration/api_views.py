"""
Microsoft Graph API Views - Delegated Permissions
Uses tokens from authenticated user session
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .services_delegated import GraphServiceDelegated
from .serializers import UserProfileSerializer


class MyProfileAPIView(APIView):
    """
    Get current authenticated user's profile from Microsoft Graph
    Requires: User must be logged in with Django and Microsoft account
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My Profile",
        description="Retrieve the authenticated user's profile from Microsoft Graph API. User must login with Microsoft first.",
        responses={
            200: UserProfileSerializer,
            401: {"description": "Not authenticated with Microsoft"},
        },
        tags=['Microsoft Graph - Delegated']
    )
    def get(self, request):
        """
        Get current user's profile
        """
        # Check if user has Microsoft Graph token
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {
                    'error': 'Not authenticated with Microsoft',
                    'message': 'Please login with your Microsoft account first',
                    'login_url': '/graph/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            graph_service = GraphServiceDelegated()
            user_data = graph_service.get_my_profile(access_token)
            
            # For read-only serializers, pass data as instance not as data parameter
            serializer = UserProfileSerializer(user_data)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_msg = str(e)
            
            # If token expired, clear it
            if '401' in error_msg or 'expired' in error_msg.lower():
                request.session.pop('graph_access_token', None)
                return Response(
                    {
                        'error': 'Token expired',
                        'message': 'Your session has expired. Please login again.',
                        'login_url': '/graph/login/'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyMessagesAPIView(APIView):
    """
    Get current user's email messages
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My Messages",
        description="Retrieve the authenticated user's recent email messages",
        responses={200: dict},
        tags=['Microsoft Graph - Delegated']
    )
    def get(self, request):
        """
        Get current user's messages
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            top = int(request.query_params.get('top', 10))
            graph_service = GraphServiceDelegated()
            messages_data = graph_service.get_my_messages(access_token, top=top)
            
            return Response(messages_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyCalendarAPIView(APIView):
    """
    Get current user's calendar events
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My Calendar",
        description="Retrieve the authenticated user's calendar events",
        responses={200: dict},
        tags=['Microsoft Graph - Delegated']
    )
    def get(self, request):
        """
        Get current user's calendar events
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            top = int(request.query_params.get('top', 10))
            graph_service = GraphServiceDelegated()
            events_data = graph_service.get_my_calendar_events(access_token, top=top)
            
            return Response(events_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
