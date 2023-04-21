from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.LoginRegister, name="LoginRegister"),
    path('userProf/<str:username>', views.userProf, name="userProf"),
    path('logout/', views.LogoutUser, name="LogoutUser"),
    path('deleteuser/<str:username>/<int:id>', views.DeleteUser, name="DeleteUser"),

    path('dash/', views.Dashboard, name="Dashboard"),
    path('athletes/', views.AthletesDash, name="AthletesDash"),
    path('maleathletes/', views.MaleAthletes, name="MaleAthletes"),
    path('femaleathletes/', views.FemaleAthletes, name="FemaleAthletes"),
    path('teamspecificathletes/<str:sport>/', views.TeamSpecificAthletes, name="TeamSpecificAthletes"),

    path('addathlete/', views.AddAthlete, name="AddAthlete"),
    path('<str:fname>/<str:lname>/<path:dob>/<int:id>', views.AthleteProf, name="AthleteProf"),
    path('/editAthlete/<str:fname>/<str:lname>/<path:dob>/<int:id>', views.EditAthlete, name="EditAthlete"),
    
    path('teams/', views.TeamDash, name="TeamDash"),
    path('recordKPI/', views.recordKPI, name="recordKPI"),
    path('addTestType/', views.addTestType, name="addTestType"),
    path('wellnessForm/', views.wellnessForm, name="wellnessForm"),
    path('wellness/', views.WellnessDash, name="WellnessDash"),
    path('/addwellness/<str:fname>/<str:lname>/<path:dob>', views.AddWellness, name="AddWellness"),
    path('/addkpi/<str:fname>/<str:lname>/<path:dob>', views.AddKPI, name="AddKPI"),
    path('deletekpi/<int:id>', views.DeleteKPI, name="DeleteKPI"),
    path('deletekpidash/<int:id>', views.DeleteKPI_Dash, name="DeleteKPI_Dash"),
    path('editkpi/<int:id>', views.EditKPI, name="EditKPI")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)