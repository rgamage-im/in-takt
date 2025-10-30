"""
QuickBooks API Views
REST API endpoints for QuickBooks data
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

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
