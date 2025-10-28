"""
QuickBooks OAuth 2.0 Views
Handles OAuth authentication flow and user interface
"""
import secrets
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views import View
from django.contrib import messages

from .services import QuickBooksService


class QuickBooksLoginView(View):
    """
    Initiate QuickBooks OAuth 2.0 flow
    Redirects user to QuickBooks authorization page
    """
    
    def get(self, request):
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['qb_oauth_state'] = state
        
        # Get authorization URL
        qb_service = QuickBooksService()
        auth_url = qb_service.get_auth_url(state=state)
        
        return redirect(auth_url)


class QuickBooksCallbackView(View):
    """
    Handle OAuth callback from QuickBooks
    Exchanges authorization code for access token
    """
    
    def get(self, request):
        # Get authorization code and state from callback
        code = request.GET.get('code')
        state = request.GET.get('state')
        realm_id = request.GET.get('realmId')  # QuickBooks company ID
        error = request.GET.get('error')
        
        # Check for errors
        if error:
            messages.error(request, f'QuickBooks authorization failed: {error}')
            return redirect('home')
        
        # Verify state token (CSRF protection)
        stored_state = request.session.get('qb_oauth_state')
        if not state or state != stored_state:
            messages.error(request, 'Invalid state parameter. Possible CSRF attack.')
            return redirect('home')
        
        # Clear state from session
        request.session.pop('qb_oauth_state', None)
        
        if not code:
            messages.error(request, 'No authorization code received from QuickBooks')
            return redirect('home')
        
        if not realm_id:
            messages.error(request, 'No company ID (realmId) received from QuickBooks')
            return redirect('home')
        
        try:
            # Exchange code for tokens
            qb_service = QuickBooksService()
            token_response = qb_service.get_token_from_code(code)
            
            # Store tokens and realm_id in session
            request.session['qb_access_token'] = token_response['access_token']
            request.session['qb_refresh_token'] = token_response['refresh_token']
            request.session['qb_realm_id'] = realm_id
            request.session['qb_token_expires_in'] = token_response.get('expires_in', 3600)
            
            messages.success(request, 'Successfully connected to QuickBooks!')
            
            # Redirect to QuickBooks dashboard
            return redirect('quickbooks:dashboard')
            
        except Exception as e:
            messages.error(request, f'Failed to connect to QuickBooks: {str(e)}')
            return redirect('home')


class QuickBooksLogoutView(View):
    """
    Disconnect from QuickBooks and clear session
    """
    
    def get(self, request):
        # Get tokens before clearing session
        access_token = request.session.get('qb_access_token')
        
        # Optionally revoke token at QuickBooks
        if access_token:
            try:
                qb_service = QuickBooksService()
                qb_service.revoke_token(access_token)
            except:
                pass  # Continue even if revocation fails
        
        # Clear QuickBooks data from session
        request.session.pop('qb_access_token', None)
        request.session.pop('qb_refresh_token', None)
        request.session.pop('qb_realm_id', None)
        request.session.pop('qb_token_expires_in', None)
        
        messages.success(request, 'Disconnected from QuickBooks')
        return redirect('home')


class QuickBooksDashboardView(View):
    """
    Display QuickBooks data dashboard
    """
    
    def get(self, request):
        # Check if user is authenticated with QuickBooks
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            messages.warning(request, 'Please connect to QuickBooks first')
            return redirect('quickbooks:qb-login')
        
        try:
            qb_service = QuickBooksService()
            
            # Fetch company info
            company_info = qb_service.get_company_info(access_token, realm_id)
            
            context = {
                'company_info': company_info.get('CompanyInfo', {}),
                'realm_id': realm_id,
            }
            
            return render(request, 'quickbooks/dashboard.html', context)
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if token expired
            if '401' in error_msg or 'Unauthorized' in error_msg:
                # Try to refresh token
                refresh_token = request.session.get('qb_refresh_token')
                if refresh_token:
                    try:
                        token_response = qb_service.refresh_access_token(refresh_token)
                        request.session['qb_access_token'] = token_response['access_token']
                        request.session['qb_refresh_token'] = token_response['refresh_token']
                        
                        # Retry fetching company info
                        company_info = qb_service.get_company_info(
                            token_response['access_token'],
                            realm_id
                        )
                        
                        context = {
                            'company_info': company_info.get('CompanyInfo', {}),
                            'realm_id': realm_id,
                        }
                        
                        return render(request, 'quickbooks/dashboard.html', context)
                    except:
                        pass
                
                # If refresh failed, redirect to login
                messages.error(request, 'Your QuickBooks session has expired. Please login again.')
                return redirect('quickbooks:qb-login')
            
            # Other errors
            context = {
                'error': f'Failed to load QuickBooks data: {error_msg}',
            }
            return render(request, 'quickbooks/dashboard.html', context)


class QuickBooksCompanyInfoView(View):
    """
    Display company information
    """
    
    def get(self, request):
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            return JsonResponse({'error': 'Not authenticated with QuickBooks'}, status=401)
        
        try:
            qb_service = QuickBooksService()
            company_info = qb_service.get_company_info(access_token, realm_id)
            return JsonResponse(company_info)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class QuickBooksInvoicesView(View):
    """
    Display invoices in a table view using Tabulator
    """
    
    def get(self, request):
        # Check if user is authenticated with QuickBooks
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            messages.warning(request, 'Please connect to QuickBooks to view invoices.')
            return redirect('quickbooks:qb-login')
        
        # Render the template - Tabulator will fetch data via AJAX
        return render(request, 'quickbooks/invoices.html')


class QuickBooksExpensesView(View):
    """
    Display expenses in a table view using Tabulator
    """
    
    def get(self, request):
        # Check if user is authenticated with QuickBooks
        access_token = request.session.get('qb_access_token')
        realm_id = request.session.get('qb_realm_id')
        
        if not access_token or not realm_id:
            messages.warning(request, 'Please connect to QuickBooks to view expenses.')
            return redirect('quickbooks:qb-login')
        
        # Render the template - Tabulator will fetch data via AJAX
        return render(request, 'quickbooks/expenses.html')
