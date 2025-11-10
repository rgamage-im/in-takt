"""
Microsoft Graph API Views - Delegated Permissions
Uses tokens from authenticated user session
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

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


class MyTeamsAPIView(APIView):
    """
    Get current user's Teams
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My Teams",
        description="Retrieve the teams the authenticated user is a member of",
        responses={200: dict},
        tags=['Microsoft Graph - Delegated']
    )
    def get(self, request):
        """
        Get current user's joined teams
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            graph_service = GraphServiceDelegated()
            teams_data = graph_service.get_my_joined_teams(access_token)
            
            return Response(teams_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyTeamsChannelMessagesAPIView(APIView):
    """
    Get channel messages from all user's teams
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My Channel Messages",
        description="Retrieve recent channel messages from all teams the user is a member of",
        responses={200: dict},
        tags=['Microsoft Graph - Delegated']
    )
    def get(self, request):
        """
        Get channel messages from all teams
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_per_channel = int(request.query_params.get('max_per_channel', 10))
            graph_service = GraphServiceDelegated()
            messages_data = graph_service.get_all_my_channel_messages(
                access_token, 
                max_messages_per_channel=max_per_channel
            )
            
            # Filter out system event messages, deleted messages, and bot messages
            if messages_data.get('teams'):
                for team in messages_data['teams']:
                    if team.get('channels'):
                        for channel in team['channels']:
                            if channel.get('messages'):
                                # Filter out unwanted messages:
                                # - System event messages (content is '<systemEventMessage/>')
                                # - Deleted messages (deletedDateTime is not None)
                                # - Bot messages (from.user is None)
                                channel['messages'] = [
                                    msg for msg in channel['messages']
                                    if msg.get('body', {}).get('content') != '<systemEventMessage/>'
                                    and msg.get('deletedDateTime') is None
                                    and msg.get('from', {}).get('user') is not None
                                ]
                
                # Recalculate total_messages after filtering
                total = 0
                for team in messages_data['teams']:
                    if team.get('channels'):
                        for channel in team['channels']:
                            total += len(channel.get('messages', []))
                messages_data['total_messages'] = total
            
            # Create response with cache-control headers to prevent caching
            response = Response(messages_data, status=status.HTTP_200_OK)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyOneDriveAPIView(APIView):
    """
    Get user's OneDrive information
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get My OneDrive",
        description="Retrieve information about the authenticated user's OneDrive",
        responses={200: dict},
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        Get current user's OneDrive info
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            graph_service = GraphServiceDelegated()
            drive_data = graph_service.get_my_drive(access_token)
            
            return Response(drive_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyDrivesListAPIView(APIView):
    """
    List all drives available to the user
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List My Drives",
        description="Retrieve all drives available to the user (OneDrive, SharePoint sites, etc.)",
        responses={200: dict},
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        List all available drives
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            graph_service = GraphServiceDelegated()
            drives_data = graph_service.list_drives(access_token)
            
            return Response(drives_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OneDriveFolderContentsAPIView(APIView):
    """
    List contents of a OneDrive folder
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List Folder Contents",
        description="""
        List files and folders in a OneDrive folder.
        
        You can specify the folder by:
        - **path**: Folder path (e.g., '/Documents' or '/Documents/Receipts')
        - **item_id**: Folder ID
        - Neither (returns root folder contents)
        
        Query parameters:
        - `path`: Folder path (e.g., 'Documents/Receipts')
        - `item_id`: Folder item ID
        - `drive_id`: Optional drive ID (uses default OneDrive if not specified)
        """,
        parameters=[
            OpenApiParameter(
                name='path',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Folder path (e.g., "Documents/Receipts")',
            ),
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Folder item ID',
            ),
            OpenApiParameter(
                name='drive_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Drive ID (optional, uses default OneDrive if not specified)',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        Get folder contents by path or ID
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            folder_path = request.query_params.get('path')
            item_id = request.query_params.get('item_id')
            drive_id = request.query_params.get('drive_id')
            
            graph_service = GraphServiceDelegated()
            
            # Priority: item_id > path > root
            if item_id:
                contents = graph_service.get_folder_contents_by_id(access_token, item_id, drive_id)
            elif folder_path:
                contents = graph_service.get_folder_contents(access_token, folder_path, drive_id)
            else:
                contents = graph_service.get_drive_root_children(access_token, drive_id)
            
            return Response(contents, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OneDriveSearchAPIView(APIView):
    """
    Search OneDrive for files and folders
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Search OneDrive",
        description="""
        Search for files and folders in OneDrive.
        
        The search query can match:
        - File names
        - Folder names
        - File content (for supported file types)
        
        Query parameters:
        - `q`: Search query (required)
        - `drive_id`: Optional drive ID (uses default OneDrive if not specified)
        - `top`: Maximum number of results (default: 50)
        """,
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True,
            ),
            OpenApiParameter(
                name='drive_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Drive ID (optional)',
            ),
            OpenApiParameter(
                name='top',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum results (default: 50)',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        Search OneDrive
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Missing required parameter: q (search query)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            drive_id = request.query_params.get('drive_id')
            top = int(request.query_params.get('top', 50))
            
            graph_service = GraphServiceDelegated()
            results = graph_service.search_onedrive(access_token, query, drive_id, top)
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OneDriveSearchAllAPIView(APIView):
    """
    Search across ALL drives (personal OneDrive + SharePoint)
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Search All Drives",
        description="""
        Search for files and folders across ALL drives accessible to the user.
        
        This includes:
        - Personal OneDrive
        - SharePoint document libraries
        - Shared drives
        
        Each result includes drive information (_driveInfo) indicating which drive it came from.
        
        Query parameters:
        - `q`: Search query (required)
        - `top`: Maximum number of results per drive (default: 50)
        
        Note: This may be slower than single-drive search as it queries multiple drives.
        """,
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True,
            ),
            OpenApiParameter(
                name='top',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum results per drive (default: 50)',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        Search all accessible drives
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Missing required parameter: q (search query)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            top = int(request.query_params.get('top', 50))
            
            graph_service = GraphServiceDelegated()
            results = graph_service.search_all_drives(access_token, query, top)
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SharePointSitesAPIView(APIView):
    """
    Get SharePoint sites the user has access to
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List SharePoint Sites",
        description="""
        Retrieve SharePoint sites the user has access to.
        
        Query parameters:
        - `search`: Optional search query to filter sites by name
        """,
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query to filter sites',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - SharePoint']
    )
    def get(self, request):
        """
        List accessible SharePoint sites
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            search_query = request.query_params.get('search')
            
            graph_service = GraphServiceDelegated()
            sites = graph_service.get_sharepoint_sites(access_token, search_query)
            
            return Response(sites, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AllAccessibleDrivesAPIView(APIView):
    """
    Get ALL drives including SharePoint document libraries
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List All Accessible Drives (OneDrive + SharePoint)",
        description="""
        Retrieve ALL drives the user has access to, including:
        - Personal OneDrive for Business
        - SharePoint site document libraries
        
        This is more comprehensive than /api/me/drives/ which only returns
        drives where the user is the owner. This endpoint includes all
        SharePoint team sites and their document libraries.
        
        Each drive includes:
        - `_source`: 'personal' or 'sharepoint'
        - `_siteName`: SharePoint site name (for SharePoint drives)
        - `_siteId`: SharePoint site ID (for SharePoint drives)
        """,
        responses={200: dict},
        tags=['Microsoft Graph - SharePoint']
    )
    def get(self, request):
        """
        List all accessible drives including SharePoint
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            graph_service = GraphServiceDelegated()
            all_drives = graph_service.list_all_accessible_drives(access_token)
            
            return Response(all_drives, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchAllDrivesIncludingSharePointAPIView(APIView):
    """
    Search across ALL drives including SharePoint
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Search All Drives + SharePoint",
        description="""
        Search for files and folders across ALL accessible drives including SharePoint.
        
        This includes:
        - Personal OneDrive for Business
        - SharePoint team site document libraries
        - Shared drives
        
        Each result includes enhanced drive information:
        - `source`: 'personal' or 'sharepoint'
        - `siteName`: SharePoint site name (for SharePoint files)
        
        Query parameters:
        - `q`: Search query (required)
        - `top`: Maximum number of results per drive (default: 50)
        """,
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True,
            ),
            OpenApiParameter(
                name='top',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum results per drive (default: 50)',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - SharePoint']
    )
    def get(self, request):
        """
        Search all accessible drives including SharePoint
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Missing required parameter: q (search query)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            top = int(request.query_params.get('top', 50))
            
            graph_service = GraphServiceDelegated()
            results = graph_service.search_all_drives_including_sharepoint(access_token, query, top)
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

