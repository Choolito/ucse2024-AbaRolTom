from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

def index(request):
    return render(request,'home.html')

def home(request):
    return render(request, 'home.html')
    