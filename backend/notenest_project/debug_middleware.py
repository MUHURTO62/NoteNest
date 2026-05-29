import logging

logger = logging.getLogger(__name__)


class DebugHostMiddleware:
    """Log incoming Host header for debugging ALLOWED_HOSTS issues."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        host = request.META.get('HTTP_HOST', 'UNKNOWN')
        logger.warning(f"Incoming Host header: {host}")
        response = self.get_response(request)
        return response
