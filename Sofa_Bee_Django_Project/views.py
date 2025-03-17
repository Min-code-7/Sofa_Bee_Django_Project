from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>欢迎来到 Sofa Bee 订单管理系统！</h1>")
