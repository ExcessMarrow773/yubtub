from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class PortRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only redirect if DEBUG is False and request is coming to port 8000
        if not settings.DEBUG and request.get_port() == 8000:
            # Reconstruct URL without port (defaults to 80)
            new_url = f"{request.scheme}://{request.get_host().split(':')[0]}{request.path}"
            if request.GET:
                new_url += f"?{request.GET.urlencode()}"
            return HttpResponsePermanentRedirect(new_url)
        
        return self.get_response(request)