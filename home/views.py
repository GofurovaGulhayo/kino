from django.shortcuts import render


def error_403(request, exception=None):
    return render(request, 'home/home/403.html')


def error_404(request, exception):
    return render(request, "home/home/404.html", {})


def error_500(request, exception=None):
    return render(request, "home/home/500.html", {})


def main_page(request):
    return render(request, 'home/home/start.html')
