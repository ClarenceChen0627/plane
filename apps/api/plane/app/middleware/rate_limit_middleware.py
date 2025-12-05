from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from plane.utils.ip_address import get_client_ip

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Default 100 requests per minute per IP
        self.rate_limit = getattr(settings, "API_RATE_LIMIT", 100) 
        self.window = 60 

    def __call__(self, request):
        if request.path.startswith("/api/"):
            try:
                ip = get_client_ip(request)
                if not ip:
                    return self.get_response(request)
                    
                key = f"rate_limit:{ip}"
                # Get current count
                count = cache.get(key)
                
                if count is not None and count >= self.rate_limit:
                    return JsonResponse(
                        {
                            "error": "Too Many Requests", 
                            "detail": "Rate limit exceeded. Please try again later."
                        }, 
                        status=429
                    )

                if count is None:
                    cache.set(key, 1, timeout=self.window)
                else:
                    try:
                        cache.incr(key)
                    except ValueError:
                        # Case where key is not found or corrupt
                        cache.set(key, 1, timeout=self.window)
                        
            except Exception:
                # Failsafe: Do not block traffic if Redis/Cache fails
                pass

        return self.get_response(request)
