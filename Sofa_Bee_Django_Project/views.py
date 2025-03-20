from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Sofa Bee Order Management System!</h1>")
