from django.shortcuts import render


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
