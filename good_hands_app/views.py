from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class MainView(View):
    def get(self, request):
        return HttpResponse("hello world")
#        return render(request, 'main_page.html')
