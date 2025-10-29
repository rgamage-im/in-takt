from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views import View


def home(request):
    """
    Home page view - your window into Takt Homes
    """
    context = {
        'title': 'In-Takt',
        'tagline': 'Your window into Takt Homes',
        'user': request.user,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    About page view
    """
    context = {
        'title': 'About In-Takt',
    }
    return render(request, 'core/about.html', context)


class LogoutView(View):
    """
    Handle user logout
    """
    def get(self, request):
        """
        Log out user and redirect to home
        """
        logout(request)
        return redirect('home')
    
    def post(self, request):
        """
        Log out user and redirect to home
        """
        logout(request)
        return redirect('home')
