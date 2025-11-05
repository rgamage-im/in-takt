"""
Authentication views for Microsoft Graph OAuth 2.0 flow
"""
import secrets
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .services_delegated import GraphServiceDelegated


class GraphLoginView(View):
    """
    Initiate Microsoft Graph OAuth login
    """
    
    def get(self, request):
        """
        Redirect user to Microsoft login page
        """
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16)
        request.session['oauth_state'] = state
        
        # Get authorization URL
        graph_service = GraphServiceDelegated()
        auth_url = graph_service.get_auth_url(state=state)
        
        return redirect(auth_url)


class GraphCallbackView(View):
    """
    Handle OAuth callback from Microsoft
    """
    
    def get(self, request):
        """
        Exchange authorization code for access token
        """
        # Verify state to prevent CSRF
        state = request.GET.get('state')
        stored_state = request.session.get('oauth_state')
        
        if not state or state != stored_state:
            return JsonResponse({'error': 'Invalid state parameter'}, status=400)
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            error = request.GET.get('error')
            error_description = request.GET.get('error_description')
            return JsonResponse({
                'error': error,
                'error_description': error_description
            }, status=400)
        
        try:
            # Exchange code for token
            graph_service = GraphServiceDelegated()
            token_response = graph_service.get_token_from_code(code)
            
            # Store tokens in session
            request.session['graph_access_token'] = token_response['access_token']
            request.session['graph_refresh_token'] = token_response.get('refresh_token')
            request.session['graph_token_expires_in'] = token_response.get('expires_in')
            
            # Clean up state
            del request.session['oauth_state']
            
            # Redirect to profile page or home
            return redirect('msgraph:my-profile-page')
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class GraphLogoutView(View):
    """
    Clear Microsoft Graph session
    """
    
    def get(self, request):
        """
        Clear tokens from session
        """
        request.session.pop('graph_access_token', None)
        request.session.pop('graph_refresh_token', None)
        request.session.pop('graph_token_expires_in', None)
        
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class MyProfilePageView(View):
    """
    Display current user's Microsoft Graph profile (HTML page)
    Requires Django authentication + MS Graph OAuth
    """
    
    def get(self, request):
        """
        Show user profile page
        """
        access_token = request.session.get('graph_access_token')
        
        context = {
            'is_authenticated': bool(access_token),
        }
        
        if access_token:
            try:
                graph_service = GraphServiceDelegated()
                profile = graph_service.get_my_profile(access_token)
                context['user_profile'] = profile  # Changed from 'profile' to 'user_profile'
            except Exception as e:
                context['error'] = str(e)
                # Token might be expired, clear it
                request.session.pop('graph_access_token', None)
        
        return render(request, 'msgraph/profile.html', context)


@method_decorator(login_required, name='dispatch')
class GraphExploreView(View):
    """
    Entry point for exploring Microsoft 365 data.
    Requires Django authentication, then handles MS Graph OAuth if needed.
    """
    
    def get(self, request):
        """
        Check if user is authenticated with Graph.
        If yes, show profile page with access to messages, calendar, etc.
        If no, redirect to login then to profile page.
        """
        access_token = request.session.get('graph_access_token')
        
        if access_token:
            # User is already authenticated, show the profile/dashboard
            return redirect('msgraph:my-profile-page')
        else:
            # User needs to authenticate first
            # Store the intended destination so we can redirect after login
            request.session['graph_next'] = 'msgraph:my-profile-page'
            return redirect('msgraph:graph-login')


@method_decorator(login_required, name='dispatch')
class TeamsMessagesTableView(View):
    """
    Display Teams channel messages in a table view using Tabulator
    Requires Django authentication + MS Graph OAuth
    """
    
    def get(self, request):
        """
        Show Teams messages table page
        """
        # Check if user is authenticated with Microsoft Graph
        access_token = request.session.get('graph_access_token')
        
        if not access_token:
            # Store intended destination and redirect to login
            request.session['graph_next'] = 'msgraph:teams-messages-table'
            return redirect('msgraph:graph-login')
        
        # Render the template - Tabulator will fetch data via AJAX
        return render(request, 'msgraph/teams_messages.html')

