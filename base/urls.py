from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.Dashboard, name="Dashboard"),

    path('athletes/', views.AthletesDash, name="AthletesDash"),
    path("<str:fname>", views.AthleteProf, name="AthleteProf"),

    path('teams/', views.TeamDash, name="TeamDash"),
    path('create/', views.CreateDash, name="CreateDash"),
    path('analyze/', views.AnalyzeDash, name="AnalyzeDash"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)