"""Health check endpoints for Azure App Service"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Simple health check endpoint for Azure health probes.
    Returns 200 OK if the application is running.
    No authentication required.
    """
    return JsonResponse({"status": "healthy", "service": "in-takt-portal"}, status=200)
