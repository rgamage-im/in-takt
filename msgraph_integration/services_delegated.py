"""
Microsoft Graph API Service - Delegated Permissions
Handles OAuth 2.0 authorization code flow for delegated permissions
"""
import os
from typing import Optional, Dict, Any
from msal import ConfidentialClientApplication
import requests


class GraphServiceDelegated:
    """
    Service class for Microsoft Graph API with delegated permissions
    Requires user authentication via OAuth 2.0 authorization code flow
    """
    
    def __init__(self):
        self.client_id = os.getenv('MICROSOFT_GRAPH_CLIENT_ID')
        self.client_secret = os.getenv('MICROSOFT_GRAPH_CLIENT_SECRET')
        self.tenant_id = os.getenv('MICROSOFT_GRAPH_TENANT_ID', 'common')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.redirect_uri = os.getenv('MICROSOFT_GRAPH_REDIRECT_URI', 'http://localhost:8000/auth/callback')
        
        # Delegated permissions (scopes)
        self.scopes = [
            "User.Read",
            "User.ReadBasic.All",
            "Calendars.Read",
            "Mail.Read",
        ]
        
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Initialize MSAL app
        self.app = ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
    
    def get_auth_url(self, state: str = None) -> str:
        """
        Get the authorization URL for user to login
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri,
        )
        return auth_url
    
    def get_token_from_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        result = self.app.acquire_token_by_authorization_code(
            code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        
        if "access_token" in result:
            return result
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            raise Exception(f"Failed to get token: {error} - {error_description}")
    
    def get_token_from_refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Get new access token using refresh token
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token response
        """
        result = self.app.acquire_token_by_refresh_token(
            refresh_token,
            scopes=self.scopes,
        )
        
        if "access_token" in result:
            return result
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            raise Exception(f"Failed to refresh token: {error} - {error_description}")
    
    def _make_request(self, endpoint: str, access_token: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to Microsoft Graph API
        
        Args:
            endpoint: API endpoint (e.g., '/me' or '/me/messages')
            access_token: User's access token
            method: HTTP method (GET, POST, etc.)
            data: Request body for POST/PATCH requests
            
        Returns:
            JSON response from API
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.graph_endpoint}{endpoint}"
        
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_my_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user's profile
        
        Args:
            access_token: User's access token
            
        Returns:
            User profile data
        """
        return self._make_request("/me", access_token)
    
    def get_my_photo(self, access_token: str) -> Optional[bytes]:
        """
        Get current user's profile photo
        
        Args:
            access_token: User's access token
            
        Returns:
            Photo bytes or None if not available
        """
        try:
            url = f"{self.graph_endpoint}/me/photo/$value"
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None
    
    def get_my_messages(self, access_token: str, top: int = 10) -> Dict[str, Any]:
        """
        Get current user's email messages
        
        Args:
            access_token: User's access token
            top: Number of messages to return
            
        Returns:
            List of messages
        """
        endpoint = f"/me/messages?$top={top}&$select=subject,from,receivedDateTime,isRead"
        return self._make_request(endpoint, access_token)
    
    def get_my_calendar_events(self, access_token: str, top: int = 10) -> Dict[str, Any]:
        """
        Get current user's calendar events
        
        Args:
            access_token: User's access token
            top: Number of events to return
            
        Returns:
            List of calendar events
        """
        endpoint = f"/me/calendar/events?$top={top}&$select=subject,start,end,location,attendees"
        return self._make_request(endpoint, access_token)
    
    def search_users(self, access_token: str, query: str, top: int = 10) -> Dict[str, Any]:
        """
        Search for users (requires User.ReadBasic.All delegated permission)
        
        Args:
            access_token: User's access token
            query: Search query
            top: Number of results
            
        Returns:
            List of matching users
        """
        endpoint = f"/users?$filter=startswith(displayName,'{query}') or startswith(mail,'{query}')&$top={top}"
        return self._make_request(endpoint, access_token)
