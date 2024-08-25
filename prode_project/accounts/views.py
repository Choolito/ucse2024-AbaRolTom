from django.shortcuts import render, redirect
from django.contrib.auth import  authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
from django.utils.translation import gettext as _

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('Cuenta creada para %(username)s. Ya puedes iniciar sesión.') % {'username': username})
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
    
def home(request):
    return render(request, 'home.html')

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Usuario o contraseña incorrectos")
        else:
            form.add_error(None, "Formulario inválido")

    return render(request, 'login.html', {'form': form})