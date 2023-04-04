from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.LoginRegister, name="LoginRegister"),

    path('dash/', views.Dashboard, name="Dashboard"),
    path('athletes/', views.AthletesDash, name="AthletesDash"),
    path('addathlete/', views.AddAthlete, name="AddAthlete"),
    path('<str:fname>/<str:lname>/<str:sportsteam>/<str:position>/<str:gender>/<path:dob>', views.AthleteProf, name="AthleteProf"),
    path('teams/', views.TeamDash, name="TeamDash"),
    path('recordKPI/', views.recordKPI, name="recordKPI"),
    path('wellness/', views.WellnessDash, name="WellnessDash"),
    path('/addwellness/<str:fname>/<str:lname>/<path:dob>', views.AddWellness, name="AddWellness"),
    path('/addkpi/<str:fname>/<str:lname>/<path:dob>', views.AddKPI, name="AddKPI"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)