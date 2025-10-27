"""
Microsoft Graph API Service
Handles authentication and API calls to Microsoft Graph
"""
import os
from typing import Optional, Dict, Any
from msal import ConfidentialClientApplication
import requests


class GraphService:
    """
    Service class for Microsoft Graph API interactions
    """
    
    def __init__(self):
        self.client_id = os.getenv('MICROSOFT_GRAPH_CLIENT_ID')
        self.client_secret = os.getenv('MICROSOFT_GRAPH_CLIENT_SECRET')
        self.tenant_id = os.getenv('MICROSOFT_GRAPH_TENANT_ID', 'common')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Initialize MSAL app
        self.app = ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get access token using client credentials flow
        """
        try:
            result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                error = result.get("error")
                error_description = result.get("error_description")
                raise Exception(f"Failed to get token: {error} - {error_description}")
        except Exception as e:
            raise Exception(f"Authentication error: {str(e)}")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to Microsoft Graph API
        
        Args:
            endpoint: API endpoint (e.g., '/users' or '/me')
            method: HTTP method (GET, POST, etc.)
            data: Request body for POST/PATCH requests
            
        Returns:
            JSON response from API
        """
        token = self._get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.graph_endpoint}{endpoint}"
        
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self, user_id: str = "me") -> Dict[str, Any]:
        """
        Get user profile from Microsoft Graph
        
        Args:
            user_id: User ID or 'me' for current user
            
        Returns:
            User profile data
            
        Note: For 'me' endpoint, requires User.Read delegated permission.
              For specific user IDs, requires User.Read.All application permission.
        """
        endpoint = f"/users/{user_id}"
        return self._make_request(endpoint)
    
    def get_user_photo(self, user_id: str = "me") -> Optional[bytes]:
        """
        Get user profile photo
        
        Args:
            user_id: User ID or 'me' for current user
            
        Returns:
            Photo bytes or None if not available
        """
        try:
            token = self._get_access_token()
            url = f"{self.graph_endpoint}/users/{user_id}/photo/$value"
            
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None
    
    def list_users(self, top: int = 10, select: str = None) -> Dict[str, Any]:
        """
        List users in the organization
        
        Args:
            top: Number of users to return (max 999)
            select: Comma-separated list of properties to return
            
        Returns:
            List of users
        """
        params = []
        if top:
            params.append(f"$top={top}")
        if select:
            params.append(f"$select={select}")
        
        query_string = "&".join(params)
        endpoint = f"/users?{query_string}" if query_string else "/users"
        
        return self._make_request(endpoint)
    
    def search_users(self, query: str, top: int = 10) -> Dict[str, Any]:
        """
        Search for users by display name or email
        
        Args:
            query: Search query
            top: Number of results to return
            
        Returns:
            List of matching users
        """
        endpoint = f"/users?$filter=startswith(displayName,'{query}') or startswith(mail,'{query}')&$top={top}"
        return self._make_request(endpoint)
