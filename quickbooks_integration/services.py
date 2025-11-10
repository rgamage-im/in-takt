"""
QuickBooks OAuth 2.0 Service
Handles authentication and API calls to QuickBooks Online API
"""
import os
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import base64


class QuickBooksService:
    """
    QuickBooks API service using OAuth 2.0 authorization code flow
    """
    
    def __init__(self):
        self.client_id = os.getenv('QUICKBOOKS_CLIENT_ID')
        self.client_secret = os.getenv('QUICKBOOKS_CLIENT_SECRET')
        self.redirect_uri = os.getenv('QUICKBOOKS_REDIRECT_URI', 'http://localhost:8000/quickbooks/callback/')
        self.environment = os.getenv('QUICKBOOKS_ENVIRONMENT', 'sandbox')
        
        # QuickBooks OAuth endpoints
        self.auth_url = 'https://appcenter.intuit.com/connect/oauth2'
        self.token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        self.revoke_url = 'https://developer.api.intuit.com/v2/oauth2/tokens/revoke'
        
        # QuickBooks API base URLs
        if self.environment == 'production':
            self.api_base_url = 'https://quickbooks.api.intuit.com/v3'
        else:
            self.api_base_url = 'https://sandbox-quickbooks.api.intuit.com/v3'
        
        # Required scopes
        self.scopes = [
            'com.intuit.quickbooks.accounting',  # Access to accounting data
        ]
    
    def get_auth_url(self, state: str = None) -> str:
        """
        Generate the authorization URL for QuickBooks OAuth flow
        
        Args:
            state: CSRF protection token
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'state': state or '',
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_token_from_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Token response containing access_token, refresh_token, realm_id, etc.
        """
        # Create Basic Auth header
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New token response
        """
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token
        
        Args:
            token: The token to revoke
            
        Returns:
            True if successful
        """
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        data = {'token': token}
        
        response = requests.post(self.revoke_url, headers=headers, json=data)
        return response.status_code == 200
    
    def _make_api_request(
        self,
        access_token: str,
        realm_id: str,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to QuickBooks API
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            endpoint: API endpoint (e.g., 'company/{realmId}/query')
            method: HTTP method
            data: Request body for POST/PUT
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        # Replace {realmId} placeholder if present
        endpoint = endpoint.replace('{realmId}', realm_id)
        
        url = f"{self.api_base_url}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )
        response.raise_for_status()
        
        return response.json()
    
    # Company Info
    def get_company_info(self, access_token: str, realm_id: str) -> Dict[str, Any]:
        """Get company information"""
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/companyinfo/{realm_id}'
        )
    
    # Customers
    def list_customers(
        self,
        access_token: str,
        realm_id: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """List customers"""
        query = f"SELECT * FROM Customer MAXRESULTS {max_results}"
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/query',
            params={'query': query}
        )
    
    def get_customer(
        self,
        access_token: str,
        realm_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        """Get a specific customer by ID"""
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/customer/{customer_id}'
        )
    
    # Invoices
    def list_invoices(
        self,
        access_token: str,
        realm_id: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """List invoices - returns most recent first"""
        query = f"SELECT * FROM Invoice ORDERBY TxnDate DESC MAXRESULTS {max_results}"
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/query',
            params={'query': query}
        )
    
    def get_invoice(
        self,
        access_token: str,
        realm_id: str,
        invoice_id: str
    ) -> Dict[str, Any]:
        """Get a specific invoice by ID"""
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/invoice/{invoice_id}'
        )
    
    # Vendors
    def list_vendors(
        self,
        access_token: str,
        realm_id: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """List vendors"""
        query = f"SELECT * FROM Vendor MAXRESULTS {max_results}"
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/query',
            params={'query': query}
        )
    
    # Expenses
    def list_expenses(
        self,
        access_token: str,
        realm_id: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """List expenses - returns most recent first"""
        query = f"SELECT * FROM Purchase WHERE PaymentType = 'Cash' ORDERBY TxnDate DESC MAXRESULTS {max_results}"
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/query',
            params={'query': query}
        )
    
    # Accounts
    def list_accounts(
        self,
        access_token: str,
        realm_id: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """List chart of accounts"""
        query = f"SELECT * FROM Account MAXRESULTS {max_results}"
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/query',
            params={'query': query}
        )
    
    # Reports
    def get_profit_and_loss(
        self,
        access_token: str,
        realm_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Profit and Loss report
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/reports/ProfitAndLoss',
            params=params
        )
    
    def get_balance_sheet(
        self,
        access_token: str,
        realm_id: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Balance Sheet report
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            date: Report date in YYYY-MM-DD format
        """
        params = {}
        if date:
            params['date'] = date
        
        return self._make_api_request(
            access_token,
            realm_id,
            f'company/{realm_id}/reports/BalanceSheet',
            params=params
        )
    
    # Attachments / Receipts
    def upload_receipt(
        self,
        access_token: str,
        realm_id: str,
        file_content: bytes,
        file_name: str,
        content_type: str = 'image/jpeg'
    ) -> Dict[str, Any]:
        """
        Upload a receipt file to QuickBooks
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            file_content: Binary file content
            file_name: Name of the file (e.g., 'receipt.jpg')
            content_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            
        Returns:
            Attachable object with ID to link to transactions
        """
        url = f"{self.api_base_url}/company/{realm_id}/upload"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }
        
        # Prepare multipart form data
        files = {
            'file_content_01': (file_name, file_content, content_type)
        }
        
        # Include metadata as a separate form field
        data = {
            'file_metadata_01': f'{{"FileName":"{file_name}","ContentType":"{content_type}"}}'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def attach_receipt_to_transaction(
        self,
        access_token: str,
        realm_id: str,
        attachable_id: str,
        transaction_type: str,
        transaction_id: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Attach an uploaded receipt to a transaction
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            attachable_id: ID from upload_receipt response
            transaction_type: Type of transaction ('Purchase', 'Bill', 'Invoice', etc.)
            transaction_id: ID of the transaction
            note: Optional note about the attachment
            
        Returns:
            Updated attachable object
        """
        url = f"{self.api_base_url}/company/{realm_id}/attachable/{attachable_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        # Get the current attachable first to update it
        get_response = requests.get(url, headers=headers)
        get_response.raise_for_status()
        attachable = get_response.json().get('Attachable', {})
        
        # Add the entity reference
        if 'AttachableRef' not in attachable:
            attachable['AttachableRef'] = []
        
        attachable['AttachableRef'].append({
            'EntityRef': {
                'type': transaction_type,
                'value': transaction_id
            }
        })
        
        if note:
            attachable['Note'] = note
        
        # Update the attachable
        update_data = {
            'Attachable': attachable
        }
        
        response = requests.post(url, headers=headers, json=update_data)
        response.raise_for_status()
        
        return response.json()
    
    def upload_and_attach_receipt(
        self,
        access_token: str,
        realm_id: str,
        file_content: bytes,
        file_name: str,
        transaction_type: str,
        transaction_id: str,
        content_type: str = 'image/jpeg',
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to upload and attach a receipt in one call
        
        Args:
            access_token: OAuth access token
            realm_id: QuickBooks company ID
            file_content: Binary file content
            file_name: Name of the file
            transaction_type: Type of transaction ('Purchase', 'Bill', 'Invoice', etc.)
            transaction_id: ID of the transaction
            content_type: MIME type
            note: Optional note about the attachment
            
        Returns:
            Attachable object with transaction reference
        """
        # Step 1: Upload the file
        upload_response = self.upload_receipt(
            access_token,
            realm_id,
            file_content,
            file_name,
            content_type
        )
        
        # Extract the attachable ID from the response
        attachable = upload_response.get('Attachable', {})
        attachable_id = attachable.get('Id')
        
        if not attachable_id:
            raise ValueError('Upload response did not contain Attachable ID')
        
        # Step 2: Attach to the transaction
        return self.attach_receipt_to_transaction(
            access_token,
            realm_id,
            attachable_id,
            transaction_type,
            transaction_id,
            note
        )
