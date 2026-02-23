from app.models import Banner

def banners(request):
    return {
        'banners': Banner.objects.filter(active=True).order_by('created_on')
    }