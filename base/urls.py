from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.Dashboard, name="Dashboard"),

    path('athletes/', views.AthletesDash, name="AthletesDash"),
    path("<str:fname>/<str:lname>/<path:dob>", views.AthleteProf, name="AthleteProf"),

    path('teams/', views.TeamDash, name="TeamDash"),
    path('recordKPI/', views.recordKPI, name="recordKPI"),
    path('wellness/', views.WellnessDash, name="WellnessDash"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)