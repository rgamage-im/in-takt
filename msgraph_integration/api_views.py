"""
Microsoft Graph API Views - Delegated Permissions
Uses tokens from authenticated user session
"""
import re
from typing import List, Dict, Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.http import HttpResponse

from .services_delegated import GraphServiceDelegated
from .serializers import UserProfileSerializer


def parse_amount_from_filename(filename):
    """
    Parse transaction amount from expense receipt filename.

    Expected format: "Name, Description, Amount.extension"
    Examples:
        - "Randy, Azure, 48.21.pdf" -> 48.21
        - "Randy, Azure, 36.pdf" -> 36.00
        - "Evan, 3D Experience, $48.00.pdf" -> 48.00
        - "Invalid Name.pdf" -> None

    Args:
        filename: The file name to parse

    Returns:
        float: The parsed amount, or None if parsing fails
    """
    if not filename:
        return None

    try:
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Split by comma and get the last part
        parts = name_without_ext.split(',')
        if len(parts) < 2:
            return None

        # Get the last part and strip whitespace
        amount_str = parts[-1].strip()

        # Remove currency symbols and common formatting characters
        # Strip $, €, £, commas, and other common currency symbols
        amount_str = amount_str.replace('$', '').replace('€', '').replace('£', '').replace(',', '').strip()

        # Try to parse as float
        amount = float(amount_str)

        # Validate it's a reasonable amount (non-negative)
        if amount < 0:
            return None

        return amount

    except (ValueError, AttributeError, IndexError):
        return None


def match_receipts_with_qb_transactions(receipts: List[Dict[str, Any]], qb_expenses: List[Dict[str, Any]]) -> None:
    """
    Match expense receipts with QuickBooks transactions by amount.
    Modifies receipts in-place to add 'qb_match_status' and 'qb_transaction_id' fields.

    Match statuses:
        - 'none': No matching QB transaction found
        - 'single': Exactly one matching QB transaction found (stores transaction ID)
        - 'multiple': Multiple matching QB transactions found

    Args:
        receipts: List of receipt file dictionaries with 'amount' field
        qb_expenses: List of QuickBooks Purchase transactions with 'TotalAmt' and 'Id' fields
    """
    # Build a map of amounts to QB transactions
    amount_to_transactions = {}
    for expense in qb_expenses:
        try:
            amount = float(expense.get('TotalAmt', 0))
            if amount > 0:
                if amount not in amount_to_transactions:
                    amount_to_transactions[amount] = []
                amount_to_transactions[amount].append(expense)
        except (ValueError, TypeError):
            continue

    # Match each receipt with QB transactions
    for receipt in receipts:
        receipt_amount = receipt.get('amount')

        if receipt_amount is None or receipt_amount <= 0:
            receipt['qb_match_status'] = 'none'
            receipt['qb_match_count'] = 0
            receipt['qb_transaction_id'] = None
            continue

        matching_transactions = amount_to_transactions.get(receipt_amount, [])
        match_count = len(matching_transactions)

        if match_count == 0:
            receipt['qb_match_status'] = 'none'
            receipt['qb_transaction_id'] = None
        elif match_count == 1:
            receipt['qb_match_status'] = 'single'
            receipt['qb_transaction_id'] = matching_transactions[0].get('Id')
        else:
            receipt['qb_match_status'] = 'multiple'
            receipt['qb_transaction_id'] = None

        receipt['qb_match_count'] = match_count


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


class ExpenseReceiptsAPIView(APIView):
    """
    Get expense receipts from SharePoint folder
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List Expense Receipts",
        description="""
        Retrieve all expense receipt files from the designated SharePoint folder.
        
        Default location: Integral Methods > Documents > Expense Receipts
        
        Query parameters:
        - `folder_id`: Override default folder ID (optional)
        - `drive_id`: Override default drive ID (optional)
        
        Returns files only (not subfolders) with download URLs and metadata.
        """,
        parameters=[
            OpenApiParameter(
                name='folder_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='SharePoint folder item ID (optional, uses default Expense Receipts folder)',
            ),
            OpenApiParameter(
                name='drive_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='SharePoint drive ID (optional, uses default Integral Methods Documents library)',
            ),
        ],
        responses={200: dict},
        tags=['Microsoft Graph - Receipts']
    )
    def get(self, request):
        """
        List expense receipt files with parsed transaction amounts and QuickBooks matching
        """
        access_token = request.session.get('graph_access_token')

        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            folder_id = request.query_params.get('folder_id')
            drive_id = request.query_params.get('drive_id')

            graph_service = GraphServiceDelegated()

            # Call with custom IDs if provided, otherwise use defaults
            if folder_id and drive_id:
                receipts = graph_service.get_expense_receipts(access_token, folder_id, drive_id)
            elif folder_id:
                receipts = graph_service.get_expense_receipts(access_token, folder_id=folder_id)
            elif drive_id:
                receipts = graph_service.get_expense_receipts(access_token, drive_id=drive_id)
            else:
                receipts = graph_service.get_expense_receipts(access_token)

            # Parse transaction amounts from filenames for all files in one pass
            if 'value' in receipts and isinstance(receipts['value'], list):
                for file in receipts['value']:
                    filename = file.get('name', '')
                    file['amount'] = parse_amount_from_filename(filename)

                # Try to match with QuickBooks transactions if user is authenticated
                qb_access_token = request.session.get('qb_access_token')
                qb_realm_id = request.session.get('qb_realm_id')

                if qb_access_token and qb_realm_id:
                    try:
                        # Import here to avoid circular dependency issues
                        from quickbooks_integration.services import QuickBooksService

                        qb_service = QuickBooksService()
                        # Fetch recent expenses (last 100)
                        qb_response = qb_service.list_expenses(qb_access_token, qb_realm_id, max_results=100)
                        qb_expenses = qb_response.get('QueryResponse', {}).get('Purchase', [])

                        # Match receipts with QB transactions
                        match_receipts_with_qb_transactions(receipts['value'], qb_expenses)
                    except Exception as qb_error:
                        # If QB matching fails, continue without matching (set all to 'none')
                        for file in receipts['value']:
                            file['qb_match_status'] = 'none'
                            file['qb_match_count'] = 0
                else:
                    # User not authenticated with QuickBooks, set all matches to 'none'
                    for file in receipts['value']:
                        file['qb_match_status'] = 'none'
                        file['qb_match_count'] = 0

            return Response(receipts, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadFileAPIView(APIView):
    """
    Download a file from OneDrive or SharePoint
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Download File",
        description="""
        Download a file from OneDrive or SharePoint by its item ID.
        
        The file will be returned as a binary download with appropriate content type.
        
        Query parameters:
        - `item_id`: File item ID (required)
        - `drive_id`: Drive ID (optional, uses default OneDrive if not specified)
        
        Example usage:
        - `/api/me/drive/download?item_id=01ABC123...`
        - `/api/me/drive/download?item_id=01ABC123...&drive_id=b!ABC123...`
        """,
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='File item ID',
                required=True,
            ),
            OpenApiParameter(
                name='drive_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Drive ID (optional, uses default OneDrive if not specified)',
            ),
        ],
        responses={
            200: {
                'description': 'File content',
                'content': {
                    'application/octet-stream': {}
                }
            },
            400: {'description': 'Missing required parameter: item_id'},
            401: {'description': 'Not authenticated with Microsoft'},
            404: {'description': 'File not found'},
            500: {'description': 'Server error'}
        },
        tags=['Microsoft Graph - OneDrive']
    )
    def get(self, request):
        """
        Download file by item ID
        """
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response(
                {'error': 'Missing required parameter: item_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            drive_id = request.query_params.get('drive_id')
            
            graph_service = GraphServiceDelegated()
            
            # Get file metadata first to get filename and mime type
            if drive_id:
                endpoint = f"/drives/{drive_id}/items/{item_id}"
            else:
                endpoint = f"/me/drive/items/{item_id}"
            
            file_metadata = graph_service._make_request(endpoint, access_token)
            filename = file_metadata.get('name', 'download')
            mime_type = file_metadata.get('file', {}).get('mimeType', 'application/octet-stream')
            
            # Download the file content
            file_content = graph_service.download_file(access_token, item_id, drive_id)
            
            # Return as HTTP response with appropriate headers
            response = HttpResponse(file_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(file_content)
            
            return response
            
        except Exception as e:
            error_message = str(e)
            
            # Handle specific error cases
            if '404' in error_message or 'not found' in error_message.lower():
                return Response(
                    {'error': 'File not found', 'details': error_message},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadReceiptToQuickBooksAPIView(APIView):
    """
    Upload an expense receipt from SharePoint to QuickBooks and attach to a transaction
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Upload Receipt from SharePoint to QuickBooks",
        description="""
        Downloads an expense receipt file from SharePoint and uploads it to QuickBooks,
        attaching it to the specified Purchase transaction in a SINGLE API call.

        The upload includes the AttachableRef in the file metadata, which attaches
        the receipt to the transaction during upload (not in a separate step).

        Request body (JSON):
        - `file_id`: SharePoint file item ID (required)
        - `drive_id`: SharePoint drive ID (required)
        - `transaction_id`: QuickBooks Purchase transaction ID from matching (required)
        - `file_name`: File name for the attachment (required)
        - `mime_type`: MIME type of the file (required)
        
        Note: The transaction_id should come from the qb_transaction_id field returned
        by the GET /graph/api/receipts/expense/ endpoint during matching.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'file_id': {'type': 'string', 'description': 'SharePoint file item ID'},
                    'drive_id': {'type': 'string', 'description': 'SharePoint drive ID'},
                    'transaction_id': {'type': 'string', 'description': 'QuickBooks transaction ID'},
                    'file_name': {'type': 'string', 'description': 'File name'},
                    'mime_type': {'type': 'string', 'description': 'MIME type'},
                },
                'required': ['file_id', 'drive_id', 'transaction_id', 'file_name', 'mime_type']
            }
        },
        responses={
            200: {'description': 'Receipt uploaded and attached successfully'},
            400: {'description': 'Missing required parameters'},
            401: {'description': 'Not authenticated'},
            500: {'description': 'Server error'}
        },
        tags=['Microsoft Graph - Receipts']
    )
    def post(self, request):
        """
        Upload receipt from SharePoint to QuickBooks
        """
        # Check authentication for both services
        graph_token = request.session.get('graph_access_token')
        qb_token = request.session.get('qb_access_token')
        qb_realm_id = request.session.get('qb_realm_id')

        if not graph_token:
            return Response(
                {'error': 'Not authenticated with Microsoft', 'login_url': '/graph/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not qb_token or not qb_realm_id:
            return Response(
                {'error': 'Not authenticated with QuickBooks', 'login_url': '/quickbooks/login/'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extract parameters
        file_id = request.data.get('file_id')
        drive_id = request.data.get('drive_id')
        transaction_id = request.data.get('transaction_id')
        file_name = request.data.get('file_name')
        mime_type = request.data.get('mime_type')

        if not all([file_id, drive_id, transaction_id, file_name, mime_type]):
            return Response(
                {'error': 'Missing required parameters: file_id, drive_id, transaction_id, file_name, mime_type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Step 1: Download file from SharePoint
            graph_service = GraphServiceDelegated()
            file_content = graph_service.download_file(graph_token, file_id, drive_id)

            # Step 2: Upload to QuickBooks WITH transaction reference in ONE call
            from quickbooks_integration.services import QuickBooksService
            qb_service = QuickBooksService()

            # Upload and attach in a single API call using AttachableRef in metadata
            upload_response = qb_service.upload_receipt(
                access_token=qb_token,
                realm_id=qb_realm_id,
                file_content=file_content,
                file_name=file_name,
                content_type=mime_type,
                transaction_type='Purchase',
                transaction_id=transaction_id,
                note=f'Uploaded from SharePoint: {file_name}'
            )

            # Debug: Log the full response
            import json
            print(f"DEBUG: QuickBooks upload response: {json.dumps(upload_response, indent=2)}")

            # Extract attachable ID - handle different response structures
            attachable_id = None
            if 'AttachableResponse' in upload_response:
                attachable_list = upload_response['AttachableResponse']
                if isinstance(attachable_list, list) and len(attachable_list) > 0:
                    attachable_id = attachable_list[0].get('Attachable', {}).get('Id')
            elif 'Attachable' in upload_response:
                attachable_id = upload_response['Attachable'].get('Id')

            if not attachable_id:
                # Return the actual response for debugging
                return Response({
                    'error': 'Upload response did not contain attachable ID',
                    'debug_response': upload_response,
                    'help': 'The QuickBooks API returned an unexpected response structure'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'success': True,
                'message': f'Receipt "{file_name}" uploaded and attached to QuickBooks transaction in one call',
                'attachable_id': attachable_id,
                'transaction_id': transaction_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to upload receipt: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

