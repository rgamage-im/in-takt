"""
QuickBooks Integration URLs
"""
from django.urls import path
from .auth_views import (
    QuickBooksLoginView,
    QuickBooksCallbackView,
    QuickBooksLogoutView,
    QuickBooksDashboardView,
    QuickBooksCompanyInfoView,
    QuickBooksInvoicesView,
    QuickBooksExpensesView,
)
from .api_views import (
    QuickBooksCustomersAPIView,
    QuickBooksInvoicesAPIView,
    QuickBooksVendorsAPIView,
    QuickBooksExpensesAPIView,
    QuickBooksAccountsAPIView,
    QuickBooksProfitLossAPIView,
    QuickBooksBalanceSheetAPIView,
    QuickBooksUploadReceiptAPIView,
    QuickBooksAttachReceiptAPIView,
)

app_name = 'quickbooks'

urlpatterns = [
    # OAuth Authentication Routes
    path('login/', QuickBooksLoginView.as_view(), name='qb-login'),
    path('callback/', QuickBooksCallbackView.as_view(), name='qb-callback'),
    path('logout/', QuickBooksLogoutView.as_view(), name='qb-logout'),
    
    # Dashboard & Data Views (HTML)
    path('dashboard/', QuickBooksDashboardView.as_view(), name='dashboard'),
    path('company-info/', QuickBooksCompanyInfoView.as_view(), name='company-info'),
    path('invoices/', QuickBooksInvoicesView.as_view(), name='invoices'),
    path('expenses/', QuickBooksExpensesView.as_view(), name='expenses'),
    
    # API Routes (JSON)
    path('api/customers/', QuickBooksCustomersAPIView.as_view(), name='api-customers'),
    path('api/invoices/', QuickBooksInvoicesAPIView.as_view(), name='api-invoices'),
    path('api/vendors/', QuickBooksVendorsAPIView.as_view(), name='api-vendors'),
    path('api/expenses/', QuickBooksExpensesAPIView.as_view(), name='api-expenses'),
    path('api/accounts/', QuickBooksAccountsAPIView.as_view(), name='api-accounts'),
    
    # Attachments API
    path('api/upload-receipt/', QuickBooksUploadReceiptAPIView.as_view(), name='api-upload-receipt'),
    path('api/attach-receipt/', QuickBooksAttachReceiptAPIView.as_view(), name='api-attach-receipt'),
    
    # Reports API
    path('api/reports/profit-loss/', QuickBooksProfitLossAPIView.as_view(), name='api-profit-loss'),
    path('api/reports/balance-sheet/', QuickBooksBalanceSheetAPIView.as_view(), name='api-balance-sheet'),
]
