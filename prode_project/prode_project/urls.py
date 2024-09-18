"""
URL configuration for prode_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from prode.views import crear_grupo, lista_partidos, detalle_partido, ranking_global, unirse_grupo, ranking_grupo, detalle_grupo
from django.conf import settings
from django.conf.urls.static import static

@login_required
def protected_page(request):
    return HttpResponse("¡Estás viendo una página protegida!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), #url app cuentas
    path('', views.index, name='index'),
    path('protected/', protected_page, name='protected'),  # Página protegida
    path('partidos/', lista_partidos, name='lista_partidos'),
    path('partido/<int:partido_id>/', detalle_partido, name='detalle_partido'),
    path('', views.home, name='home'),
    path('crear_grupo/', crear_grupo, name='crear_grupo'),
    path('unirse_grupo/<str:codigo_invitacion>/', unirse_grupo, name='unirse_grupo'),
    path('ranking', ranking_global, name='ranking_global'),
    path('rankinggrupo/<int:grupo_id>/', ranking_grupo, name='ranking_global'),
    path('grupo/<int:grupo_id>/', detalle_grupo, name='detalle_grupo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)