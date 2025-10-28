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
)
from .api_views import (
    QuickBooksCustomersAPIView,
    QuickBooksInvoicesAPIView,
    QuickBooksVendorsAPIView,
    QuickBooksExpensesAPIView,
    QuickBooksAccountsAPIView,
    QuickBooksProfitLossAPIView,
    QuickBooksBalanceSheetAPIView,
)

app_name = 'quickbooks'

urlpatterns = [
    # OAuth Authentication Routes
    path('login/', QuickBooksLoginView.as_view(), name='qb-login'),
    path('callback/', QuickBooksCallbackView.as_view(), name='qb-callback'),
    path('logout/', QuickBooksLogoutView.as_view(), name='qb-logout'),
    
    # Dashboard (HTML)
    path('dashboard/', QuickBooksDashboardView.as_view(), name='dashboard'),
    path('company-info/', QuickBooksCompanyInfoView.as_view(), name='company-info'),
    
    # API Routes (JSON)
    path('api/customers/', QuickBooksCustomersAPIView.as_view(), name='api-customers'),
    path('api/invoices/', QuickBooksInvoicesAPIView.as_view(), name='api-invoices'),
    path('api/vendors/', QuickBooksVendorsAPIView.as_view(), name='api-vendors'),
    path('api/expenses/', QuickBooksExpensesAPIView.as_view(), name='api-expenses'),
    path('api/accounts/', QuickBooksAccountsAPIView.as_view(), name='api-accounts'),
    
    # Reports API
    path('api/reports/profit-loss/', QuickBooksProfitLossAPIView.as_view(), name='api-profit-loss'),
    path('api/reports/balance-sheet/', QuickBooksBalanceSheetAPIView.as_view(), name='api-balance-sheet'),
]
