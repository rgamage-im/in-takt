"""
Microsoft Graph API Service
Handles authentication and API calls to Microsoft Graph
"""
import os
import logging
from typing import Optional, Dict, Any
from msal import ConfidentialClientApplication
import requests

logger = logging.getLogger(__name__)


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
        
        if not response.ok:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('error', {}).get('message', error_detail)
            except:
                pass
            logger.error(f"Graph API {method} {url} failed: {response.status_code} - {error_detail}")
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
    
    def create_teams_channel_subscription(
        self, 
        team_id: str, 
        channel_id: str, 
        notification_url: str,
        client_state: str,
        expiration_minutes: int = 60,
        change_types: str = "created,updated",
        lifecycle_notification_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a subscription to receive notifications for Teams channel messages.
        
        Args:
            team_id: The Teams team ID
            channel_id: The channel ID within the team
            notification_url: Your public HTTPS webhook endpoint URL
            client_state: Secret token for validating notifications
            expiration_minutes: Subscription duration in minutes (max 4230 = ~3 days)
            change_types: Comma-separated: created, updated, deleted
            lifecycle_notification_url: Optional endpoint for lifecycle notifications
            
        Returns:
            Subscription object with id, expirationDateTime, etc.
            
        Permissions Required:
            - ChannelMessage.Read.All (application permission)
        """
        from datetime import datetime, timedelta, timezone as dt_timezone
        
        # Calculate expiration (max 4230 minutes for channel messages)
        expiration_datetime = datetime.now(dt_timezone.utc) + timedelta(minutes=min(expiration_minutes, 4230))
        expiration_str = expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')
        
        resource = f"/teams/{team_id}/channels/{channel_id}/messages"
        
        subscription_data = {
            "changeType": change_types,
            "notificationUrl": notification_url,
            "resource": resource,
            "expirationDateTime": expiration_str,
            "clientState": client_state,
            "includeResourceData": False  # Set to True if you want encrypted message content
        }
        
        # Add lifecycle notification URL if provided and expiration > 1 hour
        if lifecycle_notification_url and expiration_minutes > 60:
            subscription_data["lifecycleNotificationUrl"] = lifecycle_notification_url
        
        logger.info(f"Sending subscription request to Microsoft Graph:")
        logger.info(f"  POST /subscriptions")
        logger.info(f"  Resource: {resource}")
        logger.info(f"  Notification URL: {notification_url}")
        logger.info(f"  Change types: {change_types}")
        logger.info(f"  Expiration: {expiration_str}")
        
        return self._make_request("/subscriptions", method="POST", data=subscription_data)
    
    def renew_subscription(self, subscription_id: str, expiration_minutes: int = 60) -> Dict[str, Any]:
        """
        Renew an existing subscription by updating its expiration date.
        
        Args:
            subscription_id: The subscription ID to renew
            expiration_minutes: Additional minutes to extend (max 4230)
            
        Returns:
            Updated subscription object
        """
        from datetime import datetime, timedelta, timezone as dt_timezone
        
        expiration_datetime = datetime.now(dt_timezone.utc) + timedelta(minutes=min(expiration_minutes, 4230))
        expiration_str = expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S.0000000Z')
        
        update_data = {
            "expirationDateTime": expiration_str
        }
        
        return self._make_request(f"/subscriptions/{subscription_id}", method="PATCH", data=update_data)
    
    def delete_subscription(self, subscription_id: str) -> None:
        """
        Delete a subscription.
        
        Args:
            subscription_id: The subscription ID to delete
        """
        token = self._get_access_token()
        url = f"{self.graph_endpoint}/subscriptions/{subscription_id}"
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get details of an existing subscription.
        
        Args:
            subscription_id: The subscription ID
            
        Returns:
            Subscription object
        """
        return self._make_request(f"/subscriptions/{subscription_id}")
    
    def list_subscriptions(self) -> Dict[str, Any]:
        """
        List all active subscriptions for this application.
        
        Returns:
            List of subscription objects
        """
        return self._make_request("/subscriptions")
