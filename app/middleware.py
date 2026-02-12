from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class PortRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only redirect if DEBUG is False
        if not settings.DEBUG:
            # Get the port from the Host header
            host = request.get_host()
            
            # Check if port 8000 is in the host
            if ':8000' in host:
                # Reconstruct URL without port (defaults to 80)
                new_url = f"{request.scheme}://{host.split(':')[0]}{request.path}"
                if request.GET:
                    new_url += f"?{request.GET.urlencode()}"
                return HttpResponsePermanentRedirect(new_url)
        
        return self.get_response(request)