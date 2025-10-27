"""
Microsoft Graph API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .services import GraphService
from .serializers import UserProfileSerializer, UserListSerializer


class UserProfileView(APIView):
    """
    Get user profile from Microsoft Graph
    """
    
    @extend_schema(
        summary="Get User Profile",
        description="Retrieve a user's profile from Microsoft Graph API",
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='User ID or "me" for current user',
                default='me'
            ),
        ],
        responses={200: UserProfileSerializer},
        tags=['Microsoft Graph']
    )
    def get(self, request, user_id='me'):
        """
        Get user profile by ID or 'me' for current authenticated user
        """
        try:
            graph_service = GraphService()
            user_data = graph_service.get_user_profile(user_id)
            
            serializer = UserProfileSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserListView(APIView):
    """
    List users from Microsoft Graph
    """
    
    @extend_schema(
        summary="List Users",
        description="Get a list of users from Microsoft Graph API",
        parameters=[
            OpenApiParameter(
                name='top',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of users to return (default: 10, max: 999)',
                required=False,
            ),
            OpenApiParameter(
                name='select',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Comma-separated list of properties to return',
                required=False,
            ),
        ],
        responses={200: UserListSerializer},
        tags=['Microsoft Graph']
    )
    def get(self, request):
        """
        List users in the organization
        """
        try:
            top = request.query_params.get('top', 10)
            select = request.query_params.get('select', None)
            
            graph_service = GraphService()
            users_data = graph_service.list_users(top=int(top), select=select)
            
            serializer = UserListSerializer(data=users_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSearchView(APIView):
    """
    Search for users in Microsoft Graph
    """
    
    @extend_schema(
        summary="Search Users",
        description="Search for users by display name or email",
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
                description='Number of results to return (default: 10)',
                required=False,
            ),
        ],
        responses={200: UserListSerializer},
        tags=['Microsoft Graph']
    )
    def get(self, request):
        """
        Search for users
        """
        try:
            query = request.query_params.get('q')
            if not query:
                return Response(
                    {'error': 'Search query parameter "q" is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            top = request.query_params.get('top', 10)
            
            graph_service = GraphService()
            users_data = graph_service.search_users(query=query, top=int(top))
            
            serializer = UserListSerializer(data=users_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
