from django.shortcuts import render

# Create your views here.

def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

def handler403(request, *args, **kwargs):
    return render(request, '403.html', status=403)
