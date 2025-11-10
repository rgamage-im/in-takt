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
            "ChannelMessage.Read.All",
            "Team.ReadBasic.All",
            "Files.Read",
            "Files.Read.All",
            "Sites.Read.All",  # Required for SharePoint sites
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
    
    def get_my_joined_teams(self, access_token: str) -> Dict[str, Any]:
        """
        Get teams the current user is a member of
        
        Args:
            access_token: User's access token
            
        Returns:
            List of teams
        """
        endpoint = "/me/joinedTeams"
        return self._make_request(endpoint, access_token)
    
    def get_team_channels(self, access_token: str, team_id: str) -> Dict[str, Any]:
        """
        Get channels for a specific team
        
        Args:
            access_token: User's access token
            team_id: Team ID
            
        Returns:
            List of channels
        """
        endpoint = f"/teams/{team_id}/channels"
        return self._make_request(endpoint, access_token)
    
    def get_channel_messages(self, access_token: str, team_id: str, channel_id: str, top: int = 50) -> Dict[str, Any]:
        """
        Get messages from a specific channel
        
        Args:
            access_token: User's access token
            team_id: Team ID
            channel_id: Channel ID
            top: Number of messages to return
            
        Returns:
            List of channel messages ordered by most recent first
        """
        # Note: orderby is not supported for channel messages, but we request top messages
        # which should give us the most recent by default
        endpoint = f"/teams/{team_id}/channels/{channel_id}/messages?$top={top}"
        return self._make_request(endpoint, access_token)
    
    def get_all_my_channel_messages(self, access_token: str, max_messages_per_channel: int = 10) -> Dict[str, Any]:
        """
        Get recent messages from all channels the user has access to
        
        Args:
            access_token: User's access token
            max_messages_per_channel: Maximum messages to fetch per channel
            
        Returns:
            Dictionary with teams, channels, and messages
        """
        result = {
            'teams': [],
            'total_messages': 0
        }
        
        # Get all teams user is member of
        teams_response = self.get_my_joined_teams(access_token)
        teams = teams_response.get('value', [])
        
        for team in teams:
            team_id = team.get('id')
            team_data = {
                'id': team_id,
                'displayName': team.get('displayName'),
                'channels': []
            }
            
            # Get channels for this team
            try:
                channels_response = self.get_team_channels(access_token, team_id)
                channels = channels_response.get('value', [])
                
                for channel in channels:
                    channel_id = channel.get('id')
                    channel_data = {
                        'id': channel_id,
                        'displayName': channel.get('displayName'),
                        'messages': []
                    }
                    
                    # Get messages from this channel
                    try:
                        messages_response = self.get_channel_messages(
                            access_token, 
                            team_id, 
                            channel_id, 
                            top=max_messages_per_channel
                        )
                        messages = messages_response.get('value', [])
                        channel_data['messages'] = messages
                        result['total_messages'] += len(messages)
                    except Exception as e:
                        channel_data['error'] = str(e)
                    
                    team_data['channels'].append(channel_data)
            except Exception as e:
                team_data['error'] = str(e)
            
            result['teams'].append(team_data)
        
        return result
    
    # OneDrive / Files Methods
    
    def get_my_drive(self, access_token: str) -> Dict[str, Any]:
        """
        Get information about the user's default OneDrive
        
        Args:
            access_token: User's access token
            
        Returns:
            Drive information
        """
        endpoint = "/me/drive"
        return self._make_request(endpoint, access_token)
    
    def list_drives(self, access_token: str) -> Dict[str, Any]:
        """
        List all drives available to the user
        
        Args:
            access_token: User's access token
            
        Returns:
            List of drives (OneDrive, SharePoint document libraries, etc.)
        """
        endpoint = "/me/drives"
        return self._make_request(endpoint, access_token)
    
    def get_drive_root_children(self, access_token: str, drive_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List files and folders in the root of a drive
        
        Args:
            access_token: User's access token
            drive_id: Optional drive ID (uses default drive if not provided)
            
        Returns:
            List of items in the root folder
        """
        if drive_id:
            endpoint = f"/drives/{drive_id}/root/children"
        else:
            endpoint = "/me/drive/root/children"
        
        return self._make_request(endpoint, access_token)
    
    def get_folder_contents(
        self, 
        access_token: str, 
        folder_path: str, 
        drive_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List files and folders in a specific folder by path
        
        Args:
            access_token: User's access token
            folder_path: Path to the folder (e.g., '/Documents' or '/Documents/Receipts')
            drive_id: Optional drive ID (uses default drive if not provided)
            
        Returns:
            List of items in the folder
        """
        # Remove leading/trailing slashes and normalize path
        folder_path = folder_path.strip('/')
        
        if drive_id:
            endpoint = f"/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            endpoint = f"/me/drive/root:/{folder_path}:/children"
        
        return self._make_request(endpoint, access_token)
    
    def get_folder_contents_by_id(
        self, 
        access_token: str, 
        item_id: str,
        drive_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List files and folders in a specific folder by item ID
        
        Args:
            access_token: User's access token
            item_id: The ID of the folder
            drive_id: Optional drive ID (uses default drive if not provided)
            
        Returns:
            List of items in the folder
        """
        if drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/children"
        else:
            endpoint = f"/me/drive/items/{item_id}/children"
        
        return self._make_request(endpoint, access_token)
    
    def search_onedrive(
        self, 
        access_token: str, 
        query: str,
        drive_id: Optional[str] = None,
        top: int = 50
    ) -> Dict[str, Any]:
        """
        Search for files and folders in OneDrive
        
        Args:
            access_token: User's access token
            query: Search query string
            drive_id: Optional drive ID (uses default drive if not provided)
            top: Maximum number of results to return
            
        Returns:
            Search results containing matching files and folders
        """
        if drive_id:
            endpoint = f"/drives/{drive_id}/root/search(q='{query}')?$top={top}"
        else:
            endpoint = f"/me/drive/root/search(q='{query}')?$top={top}"
        
        return self._make_request(endpoint, access_token)
    
    def get_item_by_path(
        self,
        access_token: str,
        item_path: str,
        drive_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a specific file or folder by its path
        
        Args:
            access_token: User's access token
            item_path: Path to the item (e.g., '/Documents/report.pdf')
            drive_id: Optional drive ID (uses default drive if not provided)
            
        Returns:
            Item metadata
        """
        # Remove leading/trailing slashes and normalize path
        item_path = item_path.strip('/')
        
        if drive_id:
            endpoint = f"/drives/{drive_id}/root:/{item_path}"
        else:
            endpoint = f"/me/drive/root:/{item_path}"
        
        return self._make_request(endpoint, access_token)
    
    def search_all_drives(
        self,
        access_token: str,
        query: str,
        top: int = 50
    ) -> Dict[str, Any]:
        """
        Search across ALL drives the user has access to (personal OneDrive + SharePoint)
        
        Args:
            access_token: User's access token
            query: Search query string
            top: Maximum number of results per drive (default: 50)
            
        Returns:
            Combined search results from all drives with drive metadata
        """
        # First, get all available drives
        drives_response = self.list_drives(access_token)
        drives = drives_response.get('value', [])
        
        # Search each drive and combine results
        all_results = []
        
        for drive in drives:
            drive_id = drive.get('id')
            drive_name = drive.get('name', 'Unknown')
            drive_type = drive.get('driveType', 'unknown')
            
            try:
                # Search this drive
                search_results = self.search_onedrive(access_token, query, drive_id, top)
                
                # Add drive metadata to each result
                for item in search_results.get('value', []):
                    item['_driveInfo'] = {
                        'id': drive_id,
                        'name': drive_name,
                        'type': drive_type
                    }
                    all_results.append(item)
            except Exception as e:
                # If search fails for a drive, log it but continue with other drives
                print(f"Failed to search drive {drive_name} ({drive_id}): {str(e)}")
                continue
        
        return {
            'value': all_results,
            'totalDrivesSearched': len(drives),
            'totalResults': len(all_results)
        }
    
    # SharePoint Sites Methods
    
    def get_sharepoint_sites(
        self,
        access_token: str,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get SharePoint sites the user has access to
        
        Args:
            access_token: User's access token
            search_query: Optional search query to filter sites
            
        Returns:
            List of SharePoint sites
        """
        if search_query:
            # Search for sites by name
            endpoint = f"/sites?search={search_query}"
        else:
            # Get followed/frequently accessed sites
            endpoint = "/sites?search=*"
        
        return self._make_request(endpoint, access_token)
    
    def get_site_drives(
        self,
        access_token: str,
        site_id: str
    ) -> Dict[str, Any]:
        """
        Get all document libraries (drives) for a specific SharePoint site
        
        Args:
            access_token: User's access token
            site_id: SharePoint site ID
            
        Returns:
            List of document libraries (drives) in the site
        """
        endpoint = f"/sites/{site_id}/drives"
        return self._make_request(endpoint, access_token)
    
    def list_all_accessible_drives(
        self,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get ALL drives user has access to, including:
        - Personal OneDrive
        - SharePoint site document libraries
        
        This is more comprehensive than list_drives() which only returns
        drives where the user is the owner.
        
        Args:
            access_token: User's access token
            
        Returns:
            Combined list of all accessible drives with metadata
        """
        all_drives = []
        
        # 1. Get user's personal drives (OneDrive)
        try:
            personal_drives = self.list_drives(access_token)
            for drive in personal_drives.get('value', []):
                drive['_source'] = 'personal'
                all_drives.append(drive)
        except Exception as e:
            print(f"Failed to get personal drives: {str(e)}")
        
        # 2. Get SharePoint sites and their drives
        try:
            sites_response = self.get_sharepoint_sites(access_token)
            sites = sites_response.get('value', [])
            
            for site in sites:
                site_id = site.get('id')
                site_name = site.get('displayName', site.get('name', 'Unknown'))
                
                try:
                    # Get all document libraries for this site
                    site_drives = self.get_site_drives(access_token, site_id)
                    
                    for drive in site_drives.get('value', []):
                        drive['_source'] = 'sharepoint'
                        drive['_siteName'] = site_name
                        drive['_siteId'] = site_id
                        all_drives.append(drive)
                except Exception as e:
                    print(f"Failed to get drives for site {site_name}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Failed to get SharePoint sites: {str(e)}")
        
        return {
            'value': all_drives,
            'totalDrives': len(all_drives)
        }
    
    def search_all_drives_including_sharepoint(
        self,
        access_token: str,
        query: str,
        top: int = 50
    ) -> Dict[str, Any]:
        """
        Search across ALL accessible drives including SharePoint sites
        
        This is an enhanced version of search_all_drives() that also
        includes SharePoint document libraries.
        
        Args:
            access_token: User's access token
            query: Search query string
            top: Maximum number of results per drive (default: 50)
            
        Returns:
            Combined search results from all drives with drive metadata
        """
        # Get all accessible drives (including SharePoint)
        all_drives_response = self.list_all_accessible_drives(access_token)
        drives = all_drives_response.get('value', [])
        
        # Search each drive and combine results
        all_results = []
        
        for drive in drives:
            drive_id = drive.get('id')
            drive_name = drive.get('name', 'Unknown')
            drive_type = drive.get('driveType', 'unknown')
            source = drive.get('_source', 'unknown')
            site_name = drive.get('_siteName', '')
            
            try:
                # Search this drive
                search_results = self.search_onedrive(access_token, query, drive_id, top)
                
                # Add drive metadata to each result
                for item in search_results.get('value', []):
                    item['_driveInfo'] = {
                        'id': drive_id,
                        'name': drive_name,
                        'type': drive_type,
                        'source': source,
                        'siteName': site_name
                    }
                    all_results.append(item)
            except Exception as e:
                # If search fails for a drive, log it but continue with other drives
                print(f"Failed to search drive {drive_name} ({drive_id}): {str(e)}")
                continue
        
        return {
            'value': all_results,
            'totalDrivesSearched': len(drives),
            'totalResults': len(all_results)
        }
    
    def get_expense_receipts(
        self,
        access_token: str,
        folder_id: str = "01FUFIEDFYM6C7J3SLSBDZCH3NDO7KCVRK",
        drive_id: str = "b!0F05pe1C2kK-wpKqi5Zc48axM_lpIdFNjnrGDD3PSm5M87XCUZy6TIbJKPIgDtH7"
    ) -> Dict[str, Any]:
        """
        Get all expense receipt files from the specified SharePoint folder
        
        Default folder: Integral Methods SharePoint > Documents > Expense Receipts
        
        Args:
            access_token: User's access token
            folder_id: SharePoint folder item ID (defaults to Expense Receipts folder)
            drive_id: SharePoint drive ID (defaults to Integral Methods Documents library)
            
        Returns:
            List of files in the receipts folder with metadata
        """
        # Request additional fields including parentReference for path information
        endpoint = f"/drives/{drive_id}/items/{folder_id}/children?$select=id,name,size,createdDateTime,lastModifiedDateTime,webUrl,file,createdBy,lastModifiedBy,parentReference,@microsoft.graph.downloadUrl"
        
        try:
            results = self._make_request(endpoint, access_token)
            
            # Add metadata for convenience
            files = []
            for item in results.get('value', []):
                # Only include files (not subfolders)
                if 'file' in item:
                    # Get the full path from parentReference
                    parent_ref = item.get('parentReference', {})
                    parent_path = parent_ref.get('path', '')
                    
                    # Extract the path after '/drive/root:' if present
                    if '/drive/root:' in parent_path:
                        folder_path = parent_path.split('/drive/root:')[-1]
                    else:
                        folder_path = parent_path
                    
                    # Construct full file path
                    file_path = f"{folder_path}/{item.get('name')}" if folder_path else item.get('name')
                    
                    files.append({
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'path': file_path,
                        'size': item.get('size'),
                        'createdDateTime': item.get('createdDateTime'),
                        'lastModifiedDateTime': item.get('lastModifiedDateTime'),
                        'webUrl': item.get('webUrl'),
                        'downloadUrl': item.get('@microsoft.graph.downloadUrl'),
                        'mimeType': item.get('file', {}).get('mimeType'),
                        'createdBy': item.get('createdBy', {}).get('user', {}).get('displayName'),
                        'lastModifiedBy': item.get('lastModifiedBy', {}).get('user', {}).get('displayName'),
                    })
            
            return {
                'value': files,
                'totalFiles': len(files),
                'folderInfo': {
                    'folderId': folder_id,
                    'driveId': drive_id,
                    'location': 'Integral Methods > Documents > People Stuff > Receipts'
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get expense receipts: {str(e)}")

