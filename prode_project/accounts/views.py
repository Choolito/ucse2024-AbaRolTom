from django.shortcuts import render, redirect
from django.contrib.auth import  authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.urls import reverse
from .models import EmailVerificationToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # El usuario no estará activo hasta que verifique su correo
            user.save()
            
            # Crear token de verificación
            token = EmailVerificationToken.objects.create(user=user)
            
            # Enviar correo de verificación
            verification_url = request.build_absolute_uri(
                reverse('verify_email', args=[token.token])
            )
            send_mail(
                _('Verifica tu correo electrónico'),
                _('Haz clic en el siguiente enlace para verificar tu correo: %(url)s') % {'url': verification_url},
                'noreply@tudominio.com',
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, _('Cuenta creada para %(username)s. Por favor, verifica tu correo electrónico para activar tu cuenta.') % {'username': user.username})
            return redirect('verification_sent')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    verification_token = EmailVerificationToken.objects.filter(token=token).first()
    if verification_token:
        user = verification_token.user
        user.is_active = True
        user.save()
        verification_token.delete()
        messages.success(request, _('Tu cuenta ha sido verificada. Ya puedes iniciar sesión.'))
    else:
        messages.error(request, _('El enlace de verificación es inválido o ha expirado.'))
    return redirect('login')

def verification_sent(request):
    return render(request, 'accounts/verification_sent.html')
    
def home(request):
    return render(request, 'home.html')

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    
    # Obtener el parámetro 'next' en el GET o POST, para manejar el redireccionamiento correctamente
    next_url = request.GET.get('next') or request.POST.get('next') or '/partidos/'

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(next_url)
                else:
                    form.add_error(None, "Por favor, verifica tu correo electrónico antes de iniciar sesión.")
            else:
                # Verificar si el usuario existe pero no está activo
                try:
                    user = User.objects.get(username=username)
                    if not user.is_active:
                        form.add_error(None, "Por favor, verifica tu correo electrónico antes de iniciar sesión.")
                    else:
                        form.add_error(None, "Usuario o contraseña incorrectos.")
                except User.DoesNotExist:
                    form.add_error(None, "Usuario o contraseña incorrectos.")
        else:
            pass

    return render(request, 'login.html', {'form': form})