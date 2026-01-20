"""
QuickBooks API Views
REST API endpoints for QuickBooks data
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import base64

from .services import QuickBooksService


class QuickBooksCustomersAPIView(APIView):
    """
    List customers from QuickBooks
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List QuickBooks Customers",
        description="Retrieve customers from QuickBooks. Requires QuickBooks authentication.",
        parameters=[
            OpenApiParameter(
                name='max_results',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return (default: 100)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_results = int(request.query_params.get('max_results', 100))
            qb_service = QuickBooksService()
            customers = qb_service.list_customers(access_token, realm_id, max_results)
            
            return Response(customers, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksInvoicesAPIView(APIView):
    """
    List invoices from QuickBooks
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List QuickBooks Invoices",
        description="Retrieve invoices from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='max_results',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return (default: 100)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_results = int(request.query_params.get('max_results', 100))
            qb_service = QuickBooksService()
            invoices = qb_service.list_invoices(access_token, realm_id, max_results)
            
            return Response(invoices, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksVendorsAPIView(APIView):
    """
    List vendors from QuickBooks
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List QuickBooks Vendors",
        description="Retrieve vendors from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='max_results',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return (default: 100)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_results = int(request.query_params.get('max_results', 100))
            qb_service = QuickBooksService()
            vendors = qb_service.list_vendors(access_token, realm_id, max_results)
            
            return Response(vendors, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksExpensesAPIView(APIView):
    """
    List expenses from QuickBooks
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List QuickBooks Expenses",
        description="Retrieve expenses from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='max_results',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return (default: 100)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_results = int(request.query_params.get('max_results', 100))
            qb_service = QuickBooksService()
            expenses = qb_service.list_expenses(access_token, realm_id, max_results)
            
            return Response(expenses, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksAccountsAPIView(APIView):
    """
    List chart of accounts from QuickBooks
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List QuickBooks Accounts",
        description="Retrieve chart of accounts from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='max_results',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results to return (default: 100)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            max_results = int(request.query_params.get('max_results', 100))
            qb_service = QuickBooksService()
            accounts = qb_service.list_accounts(access_token, realm_id, max_results)
            
            return Response(accounts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksProfitLossAPIView(APIView):
    """
    Get Profit and Loss report
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get Profit and Loss Report",
        description="Retrieve Profit and Loss report from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD)',
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks Reports']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            qb_service = QuickBooksService()
            report = qb_service.get_profit_and_loss(
                access_token,
                realm_id,
                start_date,
                end_date
            )
            
            return Response(report, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksBalanceSheetAPIView(APIView):
    """
    Get Balance Sheet report
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get Balance Sheet Report",
        description="Retrieve Balance Sheet report from QuickBooks",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Report date (YYYY-MM-DD)',
            ),
        ],
        responses={200: dict, 401: dict},
        tags=['QuickBooks Reports']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            report_date = request.query_params.get('date')
            
            qb_service = QuickBooksService()
            report = qb_service.get_balance_sheet(access_token, realm_id, report_date)
            
            return Response(report, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickBooksUploadReceiptAPIView(APIView):
    """
    Upload a receipt to QuickBooks and optionally attach to a transaction
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @extend_schema(
        summary="Upload Receipt to QuickBooks",
        description="""
        Upload a receipt file to QuickBooks and optionally attach it to a transaction.
        
        **For file upload (multipart/form-data):**
        - `file`: The receipt file (image or PDF)
        - `transaction_type`: Optional - Type of transaction (Purchase, Bill, Invoice, etc.)
        - `transaction_id`: Optional - ID of the transaction to attach to
        - `note`: Optional - Note about the receipt
        
        **For base64 upload (application/json):**
        ```json
        {
          "file_content": "base64_encoded_file_content",
          "file_name": "receipt.jpg",
          "content_type": "image/jpeg",
          "transaction_type": "Purchase",
          "transaction_id": "123",
          "note": "Office supplies receipt"
        }
        ```
        
        If transaction_type and transaction_id are provided, the receipt will be automatically attached.
        Otherwise, just the upload response with Attachable ID will be returned.
        """,
        responses={
            200: {
                "description": "Receipt uploaded successfully",
                "example": {
                    "Attachable": {
                        "Id": "123",
                        "FileName": "receipt.jpg",
                        "FileAccessUri": "https://...",
                        "AttachableRef": []
                    }
                }
            },
            401: {"description": "Not authenticated with QuickBooks"},
            400: {"description": "Invalid request"}
        },
        tags=['QuickBooks Attachments']
    )
    def post(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            qb_service = QuickBooksService()
            
            # Handle file upload (multipart/form-data)
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                file_content = uploaded_file.read()
                file_name = uploaded_file.name
                content_type = uploaded_file.content_type or 'application/octet-stream'
            
            # Handle base64 upload (JSON)
            elif 'file_content' in request.data:
                file_content = base64.b64decode(request.data['file_content'])
                file_name = request.data.get('file_name', 'receipt.jpg')
                content_type = request.data.get('content_type', 'image/jpeg')
            
            else:
                return Response(
                    {'error': 'No file provided. Include either "file" (multipart) or "file_content" (base64 JSON)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get optional transaction attachment parameters
            transaction_type = request.data.get('transaction_type')
            transaction_id = request.data.get('transaction_id')
            note = request.data.get('note')
            
            # If transaction details provided, upload and attach in one call
            if transaction_type and transaction_id:
                result = qb_service.upload_and_attach_receipt(
                    access_token,
                    realm_id,
                    file_content,
                    file_name,
                    transaction_type,
                    transaction_id,
                    content_type,
                    note
                )
                return Response(result, status=status.HTTP_200_OK)
            
            # Otherwise, just upload the file
            else:
                result = qb_service.upload_receipt(
                    access_token,
                    realm_id,
                    file_content,
                    file_name,
                    content_type
                )
                return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuickBooksAttachReceiptAPIView(APIView):
    """
    Attach an already-uploaded receipt to a transaction
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Attach Receipt to Transaction",
        description="""
        Attach an already-uploaded receipt (by Attachable ID) to a QuickBooks transaction.
        
        **Request Body:**
        ```json
        {
          "attachable_id": "123",
          "transaction_type": "Purchase",
          "transaction_id": "456",
          "note": "Receipt for office supplies"
        }
        ```
        """,
        request={
            "application/json": {
                "example": {
                    "attachable_id": "123",
                    "transaction_type": "Purchase",
                    "transaction_id": "456",
                    "note": "Receipt for office supplies"
                }
            }
        },
        responses={
            200: {"description": "Receipt attached successfully"},
            401: {"description": "Not authenticated with QuickBooks"},
            400: {"description": "Invalid request"}
        },
        tags=['QuickBooks Attachments']
    )
    def post(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            attachable_id = request.data.get('attachable_id')
            transaction_type = request.data.get('transaction_type')
            transaction_id = request.data.get('transaction_id')
            note = request.data.get('note')
            
            if not all([attachable_id, transaction_type, transaction_id]):
                return Response(
                    {'error': 'Missing required fields: attachable_id, transaction_type, transaction_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            qb_service = QuickBooksService()
            result = qb_service.attach_receipt_to_transaction(
                access_token,
                realm_id,
                attachable_id,
                transaction_type,
                transaction_id,
                note
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuickBooksDebugInfoAPIView(APIView):
    """
    Get debug info for testing QuickBooks API with Postman/curl
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get QuickBooks Debug Info",
        description="""
        Returns access token, realm ID, and sample curl commands for testing
        the QuickBooks API directly with Postman or curl.

        **Use this to debug upload/attach receipt issues outside of Django.**
        """,
        responses={200: dict, 401: dict},
        tags=['QuickBooks Debug']
    )
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')

        if not access_token or not realm_id:
            return Response(
                {
                    'error': 'Not authenticated with QuickBooks',
                    'login_url': '/quickbooks/login/'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        qb_service = QuickBooksService()
        environment = qb_service.environment
        api_base_url = qb_service.api_base_url

        # Sample curl commands for testing
        sample_commands = {
            "1_upload_receipt": f"""curl -X POST '{api_base_url}/company/{realm_id}/upload' \\
  -H 'Authorization: Bearer {access_token}' \\
  -H 'Accept: application/json' \\
  -F 'file_metadata_01={{"FileName":"test-receipt.jpg","ContentType":"image/jpeg"}}' \\
  -F 'file_content_01=@/path/to/your/receipt.jpg;type=image/jpeg'""",

            "2_get_attachable": f"""curl -X GET '{api_base_url}/company/{realm_id}/attachable/YOUR_ATTACHABLE_ID' \\
  -H 'Authorization: Bearer {access_token}' \\
  -H 'Accept: application/json'""",

            "3_update_attachable": f"""curl -X POST '{api_base_url}/company/{realm_id}/attachable' \\
  -H 'Authorization: Bearer {access_token}' \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "Attachable": {{
      "Id": "YOUR_ATTACHABLE_ID",
      "SyncToken": "SYNC_TOKEN_FROM_GET",
      "FileName": "test-receipt.jpg",
      "Note": "Test attachment",
      "AttachableRef": [{{
        "EntityRef": {{
          "type": "Purchase",
          "value": "YOUR_TRANSACTION_ID"
        }}
      }}]
    }}
  }}'""",

            "4_get_purchase": f"""curl -X GET '{api_base_url}/company/{realm_id}/purchase/YOUR_TRANSACTION_ID' \\
  -H 'Authorization: Bearer {access_token}' \\
  -H 'Accept: application/json'"""
        }

        return Response({
            'access_token': access_token,
            'realm_id': realm_id,
            'environment': environment,
            'api_base_url': api_base_url,
            'sample_curl_commands': sample_commands,
            'postman_tips': {
                'base_url': api_base_url,
                'auth_header': f'Bearer {access_token}',
                'steps': [
                    '1. Upload receipt using multipart/form-data',
                    '2. Get the attachable ID from response',
                    '3. GET the attachable to see its current state',
                    '4. POST update with AttachableRef to attach to transaction'
                ]
            }
        }, status=status.HTTP_200_OK)
