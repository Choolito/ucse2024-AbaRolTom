from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loguea automáticamente después de registrar
            return redirect("home")  # Redirige a la página de inicio después del registro
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
    
def home(request):
    return render(request, 'home.html')
