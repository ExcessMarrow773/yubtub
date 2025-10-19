from django.shortcuts import render
from django.http import HttpResponseNotAllowed

class Custom405Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if isinstance(response, HttpResponseNotAllowed):
            return render(request, '405.html', status=405)
        
        return response
